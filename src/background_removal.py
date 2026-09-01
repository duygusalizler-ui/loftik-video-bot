"""
rembg (hafif u2netp modeli) ile GERCEK arka plan kaldirma.

ONEMLI: Bu generative bir AI degil -- sadece on plan / arka plan
segmentasyonu (siyah-beyaz bir "maske" cikarip seffaflastirma). Urun
piksellerini hicbir sekilde degistirmez/yeniden uretmez, sadece etrafini
seffaf yapar. Ayni girdi her zaman ayni (deterministik) sonucu verir --
Veo/Wiro gibi "hayal etme" riski yoktur.
"""
from __future__ import annotations

from PIL import Image
from rembg import new_session, remove

_session = None


def _get_session():
    global _session
    if _session is None:
        # u2netp: ~4MB, hizli, kaynak dostu -- GitHub Actions'ta sorunsuz calisir
        _session = new_session("u2netp")
    return _session


def remove_background(input_path: str, output_path: str) -> str:
    img = Image.open(input_path).convert("RGB")
    out = remove(img, session=_get_session())
    out.save(output_path)
    return output_path
