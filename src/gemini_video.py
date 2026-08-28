"""
Ürün görselinden Gemini'nin video modeli (Veo) ile dikey (9:16) ürün
videosu üretir.

Referans olarak sizin paylaştığınız örnek videodaki gibi: ürün taş bir
kaide üzerinde, gün batımı ışığıyla, yavaş kamera hareketiyle gösteriliyor.

NOT: google-genai kütüphanesinin API yüzeyi zamanla değişebilir. Bu kod
Ağustos 2026 itibarıyla güncel resmi örneklere göre yazıldı. Hata alırsan
önce `pip show google-genai` ile sürümü kontrol et, sonra
https://ai.google.dev/gemini-api/docs/video adresindeki güncel örneğe bak.
"""
import time
from pathlib import Path

from google import genai
from google.genai import types

from . import config

SCENE_PROMPT = (
    "Cinematic product showcase video of the exact pair of shoes shown in the "
    "reference image (same shoe, same colorway, same design -- do not change or "
    "redesign the shoe itself). The shoes rest on a light travertine stone pedestal "
    "in a sunlit outdoor courtyard, warm golden-hour light, soft natural shadows, "
    "shallow depth of field, blurred archways in the background. Slow, smooth "
    "camera push-in with a gentle orbit around the shoes. Elegant, minimal, "
    "premium footwear advertisement style, vertical mobile-first framing. "
    "No added text, no added logos, no people."
)


def _client() -> genai.Client:
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY tanımlı değil (GitHub Secrets'a eklemeyi unutma).")
    return genai.Client(api_key=config.GEMINI_API_KEY)


def _upload_image(client: genai.Client, image_path: str):
    # google-genai sürümüne göre parametre adı değişebiliyor (file= veya path=).
    try:
        return client.files.upload(file=image_path)
    except TypeError:
        return client.files.upload(path=image_path)


def generate_product_video(image_path: str, output_path: str) -> str:
    client = _client()
    uploaded = _upload_image(client, image_path)

    try:
        operation = client.models.generate_videos(
            model=config.VIDEO_MODEL,
            prompt=SCENE_PROMPT,
            image=uploaded,
            config=types.GenerateVideosConfig(
                aspect_ratio=config.VIDEO_ASPECT_RATIO,
                number_of_videos=1,
            ),
        )
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        if "404" in msg or "NOT_FOUND" in msg:
            raise RuntimeError(
                "Gemini video modeline erisilemedi (404). Olasi sebepler: "
                "(1) VEO_MODEL adi bu API anahtarinda mevcut degil -- kontrol "
                "icin tarayicida https://generativelanguage.googleapis.com/v1beta/models?key=SENIN_KEYIN "
                "adresini ac, 'veo' ara, gecerli bir model adi sec; "
                "(2) API anahtarina bagli Cloud projesinde billing kapali olabilir. "
                "Orijinal hata: " + msg
            ) from exc
        raise

    # Video üretimi asenkron çalışıyor; operation bitene kadar bekliyoruz.
    while not operation.done:
        time.sleep(15)
        operation = client.operations.get(operation)

    if not operation.response or not operation.response.generated_videos:
        raise RuntimeError(f"Video üretimi başarısız oldu: {operation}")

    generated = operation.response.generated_videos[0]
    client.files.download(file=generated.video)
    generated.video.save(output_path)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    return output_path
