"""
Hangi ürünlerin ne zaman paylaşıldığını tutan basit JSON tabanlı durum yönetimi.

data/posted.json, GitHub Actions her çalıştığında otomatik commit'lenir.
Bu sayede aynı ürün art arda / çok sık tekrar seçilmez.
"""
import json
import os
import random
from datetime import datetime, timedelta, timezone

from . import config

TR_TZ = timezone(timedelta(hours=3))


def _load() -> dict:
    if not os.path.exists(config.STATE_FILE):
        return {"posted": []}
    with open(config.STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(state: dict) -> None:
    os.makedirs(os.path.dirname(config.STATE_FILE), exist_ok=True)
    with open(config.STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def posted_urls() -> set:
    return {entry["url"] for entry in _load()["posted"]}


def mark_posted(url: str, title: str, extra: dict | None = None) -> None:
    state = _load()
    entry = {
        "url": url,
        "title": title,
        "posted_at": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        entry.update(extra)
    state["posted"].append(entry)
    _save(state)


def posts_today() -> int:
    """TR saatine gore bugun kac icerik uretildi."""
    today = datetime.now(TR_TZ).date()
    count = 0
    for entry in _load()["posted"]:
        try:
            when = datetime.fromisoformat(entry["posted_at"]).astimezone(TR_TZ).date()
        except (KeyError, ValueError):
            continue
        if when == today:
            count += 1
    return count


def pick_candidate(catalog: list):
    """
    Daha önce paylaşılmamış rastgele bir ürün seçer.
    Katalogtaki HER ürün paylaşıldıysa, en eski kayıtların bir kısmını
    unutup havuzu tekrar açar -- otomasyon asla "yapacak ürün kalmadı"
    diye durmaz.
    """
    if not catalog:
        return None
    already = posted_urls()
    fresh = [p for p in catalog if p["url"] not in already]
    if fresh:
        # Bot sezonunda botlara oncelik ver (sezonun urunu en cok satar).
        boots = [p for p in fresh if p.get("is_boot")]
        others = [p for p in fresh if not p.get("is_boot")]
        if boots and config.boots_enabled() and (
            not others or random.random() < config.BOT_PRIORITY_IN_SEASON
        ):
            return random.choice(boots)
        return random.choice(others or fresh)

    state = _load()
    state["posted"] = state["posted"][50:]
    _save(state)
    return random.choice(catalog)
