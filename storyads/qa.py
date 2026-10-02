"""Otomatik kalite kontrolu (Gemini vision): hatali kare/klip yayina gitmesin."""
from __future__ import annotations

from . import genai, settings

QA_PROMPT = """Sen kısa video reklamları için katı bir kalite kontrolcüsün.
İlk {n_ref} görsel: ürünün GERÇEK fotoğrafı (referans){karakter_notu}.
Sonraki görsel(ler): yapay zekâyla üretilmiş sahne kare(leri).
Beklenen üslup: karakterler 3D animasyon, arka plan gerçekçi fotoğraf, ürün %100 gerçek ürün fotoğrafı gibi.
Ürün sahnede görünmeli mi: {urun_gorunur}

Kontrol et:
1. Ürün görünüyorsa referansla aynı mı (şekil, renk, taban/detaylar)? Animasyon/plastik mi duruyor (kötü)?
2. Anatomi hatası: fazla ayak/el/bacak, havada duran fazladan ürün, eriyen şekiller.
3. Uydurma logo, marka, okunur yazı var mı (olmamalı)?
4. Karakter önceki sahneyle tutarlı mı (verildiyse)?
5. Görüntü bozulması, garip yüz, mantıksız arka plan.

Sadece JSON: {{"urun_uyumu": 0-10, "anatomi": 0-10, "logo_yazi_yok": 0-10, "tutarlilik": 0-10, "hatalar": ["kısa Türkçe"], "puan": 0-10}}
"puan" = en kritik sorunun belirlediği genel puan. Fazla uzuv / fazladan ürün / logo varsa puan en fazla 4."""


def score(product_refs: list[str], candidates: list[str], urun_gorunur: bool = True,
          character_ref: str | None = None) -> dict:
    refs = list(product_refs[:2]) + ([character_ref] if character_ref else [])
    prompt = QA_PROMPT.format(
        n_ref=len(product_refs[:2]), urun_gorunur="evet" if urun_gorunur else "hayır (görünmese de olur)",
        karakter_notu=", son referans: önceki sahne (karakter tutarlılığı için)" if character_ref else "",
    )
    try:
        r = genai.text_json(prompt, refs + candidates)
        r["puan"] = int(r.get("puan", 0))
    except genai.QuotaError:
        raise
    except Exception as exc:  # noqa: BLE001
        r = {"puan": 0, "hatalar": [f"kalite kontrolü çalışmadı: {exc}"]}
    r["gecti"] = r["puan"] >= settings.QA_MIN
    return r
