"""
Otomatik kalite kontrolu (Gemini vision).

Eskiden bot gunde 5 video uretiyordu cunku cogu hataliydi ve dogru olani
elle seciyordun. Artik her sahne gorseli ve her video klibi, sitedeki GERCEK
urun fotografiyla karsilastiriliyor; 10 uzerinden puan alamayan atiliyor ve
yeniden uretiliyor. Telegram'a sadece kontrolden gecenler gelir.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from . import config, gemini_util

QA_PROMPT = """Sen bir e-ticaret reklam kalite kontrolcüsüsün.
İLK görsel: sitedeki GERÇEK ürün fotoğrafı (referans).
SONRAKİ görsel(ler): yapay zekâyla üretilmiş reklam karesi/kareleri.

Üretilen karelerdeki ayakkabıyı referansla karşılaştır ve şunları kontrol et:
1. Model/şekil aynı mı (burun, bilek yüksekliği, lastik/bağcık, topuk)?
2. Renkler aynı mı (üst malzeme VE taban rengi -- taban rengi çok önemli)?
3. Uydurma logo, yazı, desen eklenmiş mi?
4. Anatomik hata var mı (üçüncü ayak, fazla bacak/el, eriyen şekiller)?
5. Yapay zekâ olduğu belli oluyor mu? (plastik/pürüzsüz ciltler, aşırı sinematik ışık,
   HDR parlaması, fazla kusursuz/steril ortam, mantıksız arka plan detayları, eriyen yazılar,
   garip eller). Sıradan bir telefon çekimi gibi mi duruyor?
6. Genel olarak reklamda kullanılabilir mi?

Sadece şu JSON'u döndür:
{"urun_benzerligi": 0-10, "gercekcilik": 0-10, "yapay_zeka_belli_mi": 0-10, "hatalar": ["kısa Türkçe madde"], "puan": 0-10}
"yapay_zeka_belli_mi": 0 = hiç belli değil, 10 = çok belli.
"puan" = en düşük kritik değer; taban rengi yanlışsa veya fazla uzuv varsa puan en fazla 4 olsun;
yapay_zeka_belli_mi 5 veya üstüyse puan en fazla 6 olsun (güven sarsar, kullanılamaz).
"""


def _mime(path: str) -> str:
    return "image/png" if path.lower().endswith(".png") else "image/jpeg"


def score_images(reference_path: str, candidate_paths: list[str]) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=config.GEMINI_API_KEY)
    parts = [QA_PROMPT, types.Part.from_bytes(data=Path(reference_path).read_bytes(), mime_type=_mime(reference_path))]
    for p in candidate_paths:
        parts.append(types.Part.from_bytes(data=Path(p).read_bytes(), mime_type=_mime(p)))
    resp = gemini_util.generate_content(
        client,
        parts,
        types.GenerateContentConfig(response_mime_type="application/json"),
    )
    text = (resp.text or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    result = json.loads(text[text.find("{") : text.rfind("}") + 1])
    result["puan"] = int(result.get("puan", 0))
    result["gecti"] = result["puan"] >= config.QA_MIN_SCORE
    return result


def safe_score(reference_path: str, candidate_paths: list[str]) -> dict:
    """QA'nin kendisi hata verirse (kota vb.) ureteni gecirmek yerine
    temkinli davranir: puan 0, gecmedi."""
    try:
        return score_images(reference_path, candidate_paths)
    except Exception as exc:  # noqa: BLE001
        print(f"UYARI: kalite kontrolü çalışmadı ({exc})")
        return {"puan": 0, "gecti": False, "hatalar": [f"kalite kontrolü çalışmadı: {exc}"]}
