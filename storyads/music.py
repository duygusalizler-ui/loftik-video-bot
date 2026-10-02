"""Arka plan muzigi: hikayenin moduna gore kutuphaneden parca secer."""
from __future__ import annotations

import json
import random
from pathlib import Path

LIB = Path(__file__).parent / "music"


def pick(mod: str | None) -> tuple[str | None, str | None]:
    """Doner: (dosya yolu, aciklamaya eklenecek kredi satiri)."""
    try:
        tracks = json.loads((LIB / "library.json").read_text(encoding="utf-8"))["parcalar"]
    except (OSError, ValueError, KeyError):
        return None, None
    tracks = [t for t in tracks if (LIB / t["dosya"]).exists()]
    if not tracks:
        return None, None
    match = [t for t in tracks if (mod or "") in t.get("mod", [])] or tracks
    t = random.choice(match)
    return str(LIB / t["dosya"]), (t.get("kredi") or None)
