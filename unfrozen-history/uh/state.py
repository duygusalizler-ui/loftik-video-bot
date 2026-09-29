"""Bölüm durumu (episode.json) + kredi defteri (ledger.json) + bütçe korumaları.

Kurallar:
- Her üretilen iş (job) id'si kaydedilir; bitmiş bir görsel/klip asla yeniden üretilmez.
- Bir varlık için en fazla 1 tekrar deneme; sonra durulur ve uyarı verilir.
- Video başına 300, ay başına 1200 kredi; bakiye 500'ün altındaysa başlanmaz.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from . import config as C

GATES = ("script", "preview", "final", "public")


class BudgetError(RuntimeError):
    pass


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _read(path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


# ---------------- Ledger ----------------

def load_ledger() -> dict:
    return _read(C.LEDGER_PATH, {"entries": []})


def spent(episode: str | None = None, month: str | None = None) -> float:
    total = 0.0
    for e in load_ledger()["entries"]:
        if episode and e["episode"] != episode:
            continue
        if month and e["month"] != month:
            continue
        total += e["credits"]
    return round(total, 2)


def _log(entry: dict) -> None:
    led = load_ledger()
    led["entries"].append(entry)
    _write(C.LEDGER_PATH, led)


# ---------------- Episode ----------------

def ep_path(ep_id: str):
    return C.EPISODES_DIR / ep_id / "episode.json"


def load_episode(ep_id: str) -> dict:
    ep = _read(ep_path(ep_id), None)
    if ep is None:
        raise FileNotFoundError(f"Bölüm bulunamadı: {ep_id}")
    return ep


def save_episode(ep: dict) -> None:
    _write(ep_path(ep["id"]), ep)


def is_ref(n) -> bool:
    return isinstance(n, str) and not n.isdigit()


def scene(ep: dict, n) -> dict:
    """Sahne (int) ya da referans kartı (str anahtar: 'walter', 'house_inside'…)."""
    if is_ref(n):
        if n not in ep.get("refs", {}):
            raise KeyError(f"Referans yok: {n}")
        return ep["refs"][n]
    for s in ep["scenes"]:
        if s["n"] == n:
            return s
    raise KeyError(f"Sahne yok: {n}")


def asset(s: dict, kind: str) -> dict:
    return s.setdefault(kind, {"status": "pending", "attempts": []})


def cost_of(kind: str) -> float:
    return C.IMAGE_COST if kind == "image" else C.CLIP_COST


def estimate(ep: dict) -> dict:
    n = len(ep["scenes"])
    refs = ep.get("refs", {})
    remaining = 0.0
    for s in ep["scenes"]:
        for kind in ("image", "clip"):
            if asset(s, kind)["status"] != "done":
                remaining += cost_of(kind)
    for r in refs.values():
        if asset(r, "image")["status"] != "done" and r.get("generate", True):
            remaining += C.IMAGE_COST
    return {
        "scenes": n,
        "refs": len(refs),
        "full_cost": n * (C.IMAGE_COST + C.CLIP_COST)
                     + sum(C.IMAGE_COST for r in refs.values() if r.get("generate", True)),
        "remaining_cost": remaining,
        "spent": spent(episode=ep["id"]),
    }


def gate_ok(ep: dict, gate: str) -> bool:
    return bool(ep.get("gates", {}).get(gate))


def approve(ep: dict, gate: str) -> None:
    if gate not in GATES:
        raise ValueError(gate)
    ep.setdefault("gates", {})[gate] = _now()
    save_episode(ep)


def preflight(ep: dict, n: int, kind: str, balance: float) -> float:
    """Üretimden önce çağrılır. Sorun varsa BudgetError fırlatır, yoksa maliyeti döner."""
    s = scene(ep, n)
    a = asset(s, kind)
    cost = cost_of(kind)

    if not gate_ok(ep, "script"):
        raise BudgetError("Senaryo onayı (kapı 1) yok — üretim yapılamaz.")
    if is_ref(n):
        if kind != "image":
            raise BudgetError("Referans kartı sadece görseldir.")
    elif n not in ep.get("preview_scenes", []) and not gate_ok(ep, "preview"):
        raise BudgetError(f"Sahne {n} önizleme dışında ve kapı 2 onayı yok.")
    elif kind == "image" and asset(s, "image")["status"] != "done":
        missing = [r for r in s.get("refs", []) if asset(scene(ep, r), "image")["status"] != "done"]
        if missing:
            raise BudgetError(f"Sahne {n} için önce referans kartları gerekli: {missing}")
    if a["status"] == "done":
        raise BudgetError(f"Sahne {n} {kind} zaten bitti (job {a.get('job_id')}) — tekrar üretilmez.")
    if a["status"] == "running":
        raise BudgetError(f"Sahne {n} {kind} hâlâ çalışıyor (job {a.get('job_id')}) — önce sonucunu kaydet.")
    if len(a["attempts"]) > C.MAX_RETRIES_PER_ASSET:
        raise BudgetError(f"Sahne {n} {kind} deneme hakkı bitti — DUR, kontrol et.")
    if kind == "clip" and asset(s, "image")["status"] != "done":
        raise BudgetError(f"Sahne {n} için önce başlangıç görseli gerekli.")
    if balance - cost < C.MIN_BALANCE_RESERVE:
        raise BudgetError(f"Bakiye {balance} → rezerv {C.MIN_BALANCE_RESERVE} altına iner.")
    ep_spent = spent(episode=ep["id"])
    if ep_spent + cost > C.MAX_CREDITS_PER_VIDEO:
        raise BudgetError(f"Video limiti: {ep_spent} + {cost} > {C.MAX_CREDITS_PER_VIDEO}")
    m_spent = spent(month=_month())
    if m_spent + cost > C.MAX_CREDITS_PER_MONTH:
        raise BudgetError(f"Aylık limit: {m_spent} + {cost} > {C.MAX_CREDITS_PER_MONTH}")
    return cost


def record_submit(ep: dict, n: int, kind: str, job_id: str, credits: float) -> None:
    """İş gönderildiği anda kaydet (kesinti olsa bile job id kaybolmaz)."""
    a = asset(scene(ep, n), kind)
    if any(t["job_id"] == job_id for t in a["attempts"]):
        return  # idempotent
    a["attempts"].append({"job_id": job_id, "submitted": _now(), "credits": credits})
    a["status"] = "running"
    a["job_id"] = job_id
    save_episode(ep)
    _log({"ts": _now(), "month": _month(), "episode": ep["id"], "scene": n,
          "kind": kind, "job_id": job_id, "credits": credits, "event": "submit"})


def record_result(ep: dict, n: int, kind: str, job_id: str, ok: bool,
                  url: str | None = None, refunded: bool = False) -> None:
    a = asset(scene(ep, n), kind)
    if a.get("job_id") != job_id:
        raise ValueError(f"Beklenen job {a.get('job_id')}, gelen {job_id}")
    a["status"] = "done" if ok else "failed"
    if url:
        a["url"] = url
    a["finished"] = _now()
    save_episode(ep)
    if not ok and refunded:
        credits = next(t["credits"] for t in a["attempts"] if t["job_id"] == job_id)
        _log({"ts": _now(), "month": _month(), "episode": ep["id"], "scene": n,
              "kind": kind, "job_id": job_id, "credits": -credits, "event": "refund"})
