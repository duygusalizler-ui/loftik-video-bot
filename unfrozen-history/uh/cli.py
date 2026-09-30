"""Unfrozen History komut satırı.

Higgsfield üretimi Claude Code oturumunda MCP ile yapılır; bu araç her üretimden
önce bütçe kontrolü yapar ve her job id'yi kaydeder.

  python -m uh.cli status ep001
  python -m uh.cli approve ep001 script
  python -m uh.cli check ep001 3 image --balance 2764.9     # prompt + parametreleri yazar
  python -m uh.cli submitted ep001 3 image <job_id>
  python -m uh.cli result ep001 3 image <job_id> --ok --url <url>
  python -m uh.cli tts ep001
  python -m uh.cli render ep001 --scenes 1-3 [--music path.mp3]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import config as C
from . import state as S


def _scenes(spec: str | None) -> list[int] | None:
    if not spec:
        return None
    out = []
    for part in spec.split(","):
        a, _, b = part.partition("-")
        out += list(range(int(a), int(b or a) + 1))
    return out


def _n(v: str):
    return int(v) if v.isdigit() else v


def ref_media(ep: dict, keys: list[str], role: str) -> list[dict]:
    out = []
    for k in keys:
        a = S.asset(S.scene(ep, k), "image")
        out.append({"role": role, "value": a.get("media_id") or a["job_id"]})
    return out


def full_prompt(ep: dict, s: dict, kind: str) -> str:
    if S.is_ref(s.get("n")):
        style = C.REF_STYLE if s["kind"] == "character" else C.STYLE
        return f"{s['prompt']}. {ep['setting']}. Style: {style}."
    if kind == "image":
        pov = f" {C.POV_HINT}." if s.get("pov") else ""
        lead = C.REF_LEAD + " " if s.get("refs") else ""
        return f"{lead}{s['image_prompt']}.{pov} {ep['setting']}. Style: {C.STYLE}."
    shots = " ".join(f"Shot {i}: {t}." for i, t in enumerate(s["shots"], 1))
    return (f"Multi-shot sequence, about 5 seconds per shot. {shots} {C.MOTION_SUFFIX}. "
            f"Sound: {s['sound']}. {C.SOUND_SUFFIX}.")


def cmd_status(a):
    ep = S.load_episode(a.ep)
    est = S.estimate(ep)
    print(f"{ep['id']} — {ep['title']}")
    print(f"Kapılar: " + ", ".join(f"{g}={'✓' if S.gate_ok(ep, g) else '·'}" for g in S.GATES))
    print(f"Sahne: {est['scenes']} | tam maliyet: {est['full_cost']} | kalan: {est['remaining_cost']} "
          f"| harcanan: {est['spent']} | aylık: {S.spent(month=S._month())}")
    for s in ep["scenes"]:
        i, c = S.asset(s, "image"), S.asset(s, "clip")
        words = len(s["narration"].split())
        print(f"  {s['n']:>2} [{words:>2} kelime] görsel={i['status']:<7} klip={c['status']:<7} {s['title']}")
    for k, r in ep.get("refs", {}).items():
        print(f"  ref {k:<13} {r['kind']:<9} görsel={S.asset(r, 'image')['status']}")


def cmd_check(a):
    ep = S.load_episode(a.ep)
    try:
        cost = S.preflight(ep, a.n, a.kind, a.balance)
    except S.BudgetError as e:
        print(f"DUR: {e}")
        sys.exit(1)
    s = S.scene(ep, a.n)
    params = dict(C.IMAGE_PARAMS if a.kind == "image" else C.VIDEO_PARAMS)
    params["model"] = C.IMAGE_MODEL if a.kind == "image" else C.VIDEO_MODEL
    params["prompt"] = full_prompt(ep, s, a.kind)
    if a.kind == "clip":
        params["medias"] = [{"role": "start_image", "value": S.asset(s, "image")["job_id"]}]
        chars = [r for r in s.get("refs", []) if ep["refs"][r]["kind"] == "character"]
        params["medias"] += ref_media(ep, chars[:3], "image_references")
    elif S.is_ref(a.n):
        params["medias"] = [{"role": "image", "value": v} for v in s.get("from", [])]
    elif s.get("refs"):
        params["medias"] = ref_media(ep, s["refs"], "image")
    if not params.get("medias"):
        params.pop("medias", None)
    print(json.dumps({"ok": True, "cost": cost, "params": params}, ensure_ascii=False, indent=2))


def cmd_submitted(a):
    ep = S.load_episode(a.ep)
    S.record_submit(ep, a.n, a.kind, a.job_id, S.cost_of(a.kind))
    print("kaydedildi")


def cmd_result(a):
    ep = S.load_episode(a.ep)
    S.record_result(ep, a.n, a.kind, a.job_id, a.ok, a.url, a.refunded)
    print("kaydedildi")


def cmd_approve(a):
    ep = S.load_episode(a.ep)
    S.approve(ep, a.gate)
    print(f"{a.gate} onaylandı")


def cmd_tts(a):
    from .tts import narrate
    ep = S.load_episode(a.ep)
    d = narrate(ep)
    for n, sec in d.items():
        print(f"  {n:>2}: {sec:5.1f} sn")
    print(f"Toplam anlatım: {sum(d.values()) / 60:.1f} dk")


def description(ep: dict) -> str:
    """İlk 2 satır videoya özel + anahtar kelime (arama sonucunda görünen kısım)."""
    src = "\n".join(f"• {s}" for s in ep["sources"])
    return (f"{ep['hook_description']}\n\n"
            f"History, lived from the inside. Every episode is told by one ordinary person "
            f"living through a hard season of the past.\n\n{ep['disclosure']}\n\n"
            f"Sources & further reading:\n{src}\n"
            + (f"\n{ep['music_credit']}\n" if ep.get("music_credit") else ""))


def cmd_doc(a):
    """Kapı 1 için okunabilir senaryo + sahne listesi (SCRIPT.md)."""
    ep = S.load_episode(a.ep)
    est = S.estimate(ep)
    lines = [f"# {ep['title']}", "", f"**Anlatıcı:** {ep['character']}", "",
             f"**Kapak:** {ep['thumbnail']}", "",
             f"**Sahne:** {est['scenes']} · **Tahmini maliyet:** {est['full_cost']} kredi · "
             f"**Önizleme sahneleri:** {ep['preview_scenes']}", ""]
    for s in ep["scenes"]:
        if s.get("beat"):
            lines += [f"### ⚡ {s['beat']}", ""]
        lines += [f"## {s['n']}. {s['title']}{' (POV)' if s['pov'] else ''}", "",
                  f"> {s['narration']}", "", f"- **Başlangıç karesi:** {s['image_prompt']}"]
        lines += [f"- **Açı {i}:** {t}" for i, t in enumerate(s["shots"], 1)]
        lines += [f"- **Ses:** {s['sound']}", ""]
    lines += ["## YouTube açıklaması (taslak)", "", "```", description(ep).strip(), "```", ""]
    out = S.ep_path(a.ep).with_name("SCRIPT.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(out)


def cmd_render(a):
    from .assemble import assemble
    ep = S.load_episode(a.ep)
    scenes = _scenes(a.scenes)
    if scenes is None and not S.gate_ok(ep, "preview"):
        print("DUR: tam render için kapı 2 (preview) onayı gerekli")
        sys.exit(1)
    assemble(ep, scenes, Path(a.music) if a.music else None, out_name=a.out)


def main():
    p = argparse.ArgumentParser(prog="uh")
    sub = p.add_subparsers(dest="cmd", required=True)

    x = sub.add_parser("status"); x.add_argument("ep"); x.set_defaults(f=cmd_status)
    x = sub.add_parser("approve"); x.add_argument("ep"); x.add_argument("gate", choices=S.GATES); x.set_defaults(f=cmd_approve)
    for name, fn in (("check", cmd_check), ("submitted", cmd_submitted), ("result", cmd_result)):
        x = sub.add_parser(name); x.add_argument("ep"); x.add_argument("n", type=_n)
        x.add_argument("kind", choices=("image", "clip")); x.set_defaults(f=fn)
        if name == "check":
            x.add_argument("--balance", type=float, required=True)
        else:
            x.add_argument("job_id")
        if name == "result":
            x.add_argument("--ok", action="store_true"); x.add_argument("--url")
            x.add_argument("--refunded", action="store_true")
    x = sub.add_parser("tts"); x.add_argument("ep"); x.set_defaults(f=cmd_tts)
    x = sub.add_parser("doc"); x.add_argument("ep"); x.set_defaults(f=cmd_doc)
    x = sub.add_parser("render"); x.add_argument("ep"); x.add_argument("--scenes")
    x.add_argument("--music"); x.add_argument("--out"); x.set_defaults(f=cmd_render)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
