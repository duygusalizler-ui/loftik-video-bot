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
    "Static product showcase video of the exact PAIR of shoes shown in the "
    "reference image (same shoe, same colorway, same design -- do not change or "
    "redesign the shoe itself). BOTH shoes of the pair -- the left shoe AND the "
    "right shoe -- must be shown together, side by side, clearly visible in every "
    "single frame of the video from start to end. Never show only one shoe alone "
    "at any point. The camera itself is completely FIXED and STATIC -- it does not "
    "move, pan, orbit, or zoom at all throughout the whole video. The pair of shoes "
    "sits together on top of a round matte white rotating display podium -- a "
    "simple circular turntable pedestal, like a professional product-photography "
    "spinning stand. Only this turntable slowly rotates a full 360 degrees, "
    "carrying both shoes around together in place, showing all angles of the pair "
    "one by one, while the camera stays locked in one fixed position the entire "
    "time and both shoes stay fully in frame together throughout. Soft "
    "studio-style lighting, shallow depth of field, softly blurred background "
    "(the background style itself can vary, that part does not matter). Elegant, "
    "minimal, premium footwear advertisement style, vertical mobile-first framing. "
    "No added text, no added logos. "
    "IMPORTANT: no people, no human body parts, no foot, no leg, no ankle, no skin "
    "anywhere in the video, not even in the first frame -- only the pair of shoes "
    "themselves, both together, resting on the rotating podium, from the very "
    "start of the video to the end."
)

CLEANUP_PROMPT = (
    "This photo shows a PAIR of shoes being worn on a person's feet/legs (or a "
    "single shoe -- work with whatever is shown). Create a clean product-only "
    "version of this exact shoe: completely remove the foot, leg, ankle, skin, "
    "sock and any clothing. Keep the shoe itself pixel-accurate -- same color, "
    "same material, same logos, same laces, same design, unchanged. "
    "IMPORTANT: if the original photo shows two shoes (a pair), the output MUST "
    "also show both shoes together, side by side -- do not drop, hide, crop out, "
    "or omit either shoe. If the original photo only shows a single shoe, you may "
    "mirror it to create a matching second shoe so the output shows a complete "
    "pair, keeping the same exact design, color and material for both. Show the "
    "pair sitting naturally together, "
    "as professional e-commerce product photography on a plain light neutral "
    "background with soft studio lighting. No people, no body parts, no text."
)


def _client() -> genai.Client:
    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY tanımlı değil (GitHub Secrets'a eklemeyi unutma).")
    return genai.Client(api_key=config.GEMINI_API_KEY)


def clean_product_shot(image_path: str, output_path: str) -> str:
    """
    Sitedeki ürün fotoğrafları genelde ayakta giyili çekiliyor. Bu fonksiyon
    Gemini'nin görsel düzenleme modeliyle (gemini-2.5-flash-image) fotoğrafı
    "sadece ürün, ayak/bacak yok" haline getirir. Video ve hikaye görseli bu
    TEMİZ fotoğraftan üretilir; böylece video hiçbir karede "giyili" görünmez.
    """
    client = _client()
    image_bytes = Path(image_path).read_bytes()
    mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"

    response = client.models.generate_content(
        model="gemini-2.5-flash-image",
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime),
            CLEANUP_PROMPT,
        ],
        config=types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"]),
    )

    for part in response.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline is not None and getattr(inline, "data", None):
            Path(output_path).write_bytes(inline.data)
            return output_path

    raise RuntimeError("Gemini gorsel duzenleme yaniti bir resim icermiyor.")


def generate_product_video(image_path: str, output_path: str) -> str:
    client = _client()

    # NOT: generate_videos'un image= parametresi, files.upload() ile alinan
    # bir dosya referansi degil, base64 goruntu byte'lari + mimeType icermeli
    # ("Input instance with `image` should contain both `bytesBase64Encoded`
    # and `mimeType`" hatasi bunun icin cikiyordu).
    image_bytes = Path(image_path).read_bytes()
    mime = "image/png" if image_path.lower().endswith(".png") else "image/jpeg"
    image_arg = types.Image(image_bytes=image_bytes, mime_type=mime)

    try:
        operation = client.models.generate_videos(
            model=config.VIDEO_MODEL,
            prompt=SCENE_PROMPT,
            image=image_arg,
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
