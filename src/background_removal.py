"""
rembg (hafif u2netp modeli) ile GERCEK arka plan kaldirma.

ONEMLI: Bu generative bir AI degil -- sadece on plan / arka plan
segmentasyonu (siyah-beyaz bir "maske" cikarip seffaflastirma). Urun
piksellerini hicbir sekilde degistirmez/yeniden uretmez, sadece etrafini
seffaf yapar. Ayni girdi her zaman ayni (deterministik) sonucu verir --
Veo/Wiro gibi "hayal etme" riski yoktur.
"""
from __future__ import annotations


def remove_background(input_path: str, output_path: str) -> str:
    # rembg/onnxruntime importu BURADA (fonksiyon icinde) yapiliyor --
    # boylece bu kutuphanede bir sorun olsa bile (ornegin eksik sistem
    # kutuphanesi), sadece BU fonksiyon cagrildiginda hata verir, tum
    # main.py'nin import asamasinda cokmesine sebep olmaz. main.py zaten
    # bu fonksiyonu try/except ile cagiriyor.
    from PIL import Image
    from rembg import new_session, remove

    session = new_session("u2netp")  # hafif model (~4MB)
    img = Image.open(input_path).convert("RGB")
    out = remove(img, session=session)
    out.save(output_path)
    return output_path
