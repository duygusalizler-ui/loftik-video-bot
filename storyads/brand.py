"""Marka ayarlari: brands/<kod>.json. Yeni musteri = yeni dosya."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

BRANDS_DIR = Path(__file__).parent / "brands"


@dataclass
class Brand:
    kod: str
    ad: str
    site: str
    sektor: str
    hedef_kitle: str
    ses_tonu: str = "samimi, esprili, Türkçe sokak dili ama kaba değil"
    bio_cta: str = "Link bio'da"
    hashtagler: list = field(default_factory=list)
    karakterler: list = field(default_factory=list)  # bos = havuzdan sec
    yasak: list = field(default_factory=list)  # asla yapilmayacaklar
    urun_notlari: dict = field(default_factory=dict)  # urun tipi -> gorsel ipucu
    muzik_modu: str = "komik"
    guven_satiri: str = ""  # açıklamaya eklenen güven satırı (kapıda ödeme, kargo, değişim)
    dil: str = "tr"


def load(kod: str) -> Brand:
    path = BRANDS_DIR / f"{kod}.json"
    if not path.exists():
        raise SystemExit(f"Marka ayarı bulunamadı: {path} (brands/_ornek.json'u kopyalayıp doldur)")
    data = json.loads(path.read_text(encoding="utf-8"))
    data.pop("_aciklama", None)
    return Brand(kod=kod, **data)
