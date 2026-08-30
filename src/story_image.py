"""
Instagram/Telegram hikayesinde paylaşılmaya hazır, dikey (1080x1920) marka
şablonlu bir görsel üretir. Ürün adı, fiyat ve siteye yönlendiren bir çağrı
metni içerir.

Not: Instagram'ın hikaye paylaşımında tıklanabilir "link sticker" eklemek
Graph API üzerinden hesap tipine göre kısıtlı olabilir -- bu yüzden linki
görselin üzerine yazıyoruz, siz hikayeyi paylaşırken link sticker'ı elle
ekleyebilirsiniz.
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

CANVAS_SIZE = (1080, 1920)
POST_CANVAS_SIZE = (1080, 1350)  # Instagram feed icin onerilen 4:5 dikey oran
BACKGROUND_COLOR = (18, 18, 18)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in (
        "DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def build_story_image(product_image_path: str, title: str, price_text, output_path: str) -> str:
    canvas = Image.new("RGB", CANVAS_SIZE, color=BACKGROUND_COLOR)

    product_img = Image.open(product_image_path).convert("RGB")
    product_img = ImageOps.contain(product_img, (1000, 1300))
    px = (CANVAS_SIZE[0] - product_img.width) // 2
    py = 280
    canvas.paste(product_img, (px, py))

    draw = ImageDraw.Draw(canvas)
    brand_font = _load_font(54)
    title_font = _load_font(38)
    cta_font = _load_font(36)

    draw.text((60, 90), "LOFTİK AYAKKABI", font=brand_font, fill=(255, 255, 255))

    text_y = py + product_img.height + 60
    draw.text((60, text_y), title, font=title_font, fill=(230, 230, 230))
    if price_text:
        draw.text((60, text_y + 60), str(price_text), font=title_font, fill=(255, 200, 110))

    draw.text(
        (60, CANVAS_SIZE[1] - 130),
        "Linke tıkla, siteden incele ↑",
        font=cta_font,
        fill=(255, 255, 255),
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=92)
    return output_path


def build_post_image(product_image_path: str, title: str, price_text, output_path: str) -> str:
    """
    Instagram FEED gönderisi için (video değil, hikaye değil) -- 4:5 dikey,
    marka şablonlu görsel. product_image_path olarak HAM (AI'dan geçmemiş,
    sitedeki orijinal) fotoğraf verilmeli -- bu fonksiyon hiçbir AI
    üretim/düzenleme adımı içermez, sadece PIL ile metin bindirir. Yani
    ürün üzerinde hiçbir detay (toka, desen, renk) değişmez -- tam olarak
    sitedeki gibi görünür.
    """
    canvas = Image.new("RGB", POST_CANVAS_SIZE, color=BACKGROUND_COLOR)

    product_img = Image.open(product_image_path).convert("RGB")
    product_img = ImageOps.contain(product_img, (1000, 950))
    px = (POST_CANVAS_SIZE[0] - product_img.width) // 2
    py = 170
    canvas.paste(product_img, (px, py))

    draw = ImageDraw.Draw(canvas)
    brand_font = _load_font(48)
    title_font = _load_font(34)
    cta_font = _load_font(32)

    draw.text((50, 60), "LOFTİK AYAKKABI", font=brand_font, fill=(255, 255, 255))

    text_y = py + product_img.height + 50
    draw.text((50, text_y), title, font=title_font, fill=(230, 230, 230))
    if price_text:
        draw.text((50, text_y + 50), str(price_text), font=title_font, fill=(255, 200, 110))

    draw.text(
        (50, POST_CANVAS_SIZE[1] - 100),
        "Sipariş vermek için bio'daki linke tıkla 👆",
        font=cta_font,
        fill=(255, 255, 255),
    )

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, quality=92)
    return output_path
