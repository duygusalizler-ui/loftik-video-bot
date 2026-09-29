"""
Gemini metin/gorsel-analiz cagrilari icin ortak yardimci.

Google eski modelleri zamanla kapatiyor (ör. 2026-09'da gemini-2.5-flash yeni
kullanicilara 404 donmeye basladi). Bu yuzden sirayla birkac model denenir;
404 / NOT_FOUND alinirsa bir sonrakine gecilir.
"""
from __future__ import annotations

from . import config


def text_models() -> list[str]:
    models = [config.GEMINI_TEXT_MODEL] + config.GEMINI_TEXT_FALLBACKS
    return list(dict.fromkeys(m for m in models if m))


def generate_content(client, contents, cfg=None):
    last_exc = None
    for model in text_models():
        try:
            return client.models.generate_content(model=model, contents=contents, config=cfg)
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            if "404" in msg or "NOT_FOUND" in msg:
                print(f"UYARI: Gemini modeli '{model}' kullanılamıyor, sıradaki deneniyor.")
                last_exc = exc
                continue
            raise
    raise last_exc or RuntimeError("Kullanılabilir Gemini metin modeli bulunamadı.")
