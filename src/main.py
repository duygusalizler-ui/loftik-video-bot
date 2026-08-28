"""
Ana akış:

1. Kategorilerdeki ürün linklerini topla (BOT kategorisi hariç)
2. Daha önce paylaşılmamış rastgele bir ürün seç
3. Seçilen ürünün detayını çek (görsel, marka, fiyat)
4. Ana ürün görselini indir
5. Görseli "ayaksız" ürün fotoğrafına çevir (en fazla 3 deneme)
6. Gemini (Veo) ile dikey (9:16) ürün videosu üret
7. Instagram/Telegram hikayesi için dikey görsel üret
8. Açıklama + hashtag oluştur
9. Telegram'a video + hikaye görselini gönder
10. data/posted.json dosyasını güncelle (GitHub Actions bunu commit'ler)

Çalıştırmak için: python -m src.main
"""
import sys
import tempfile

from . import caption as caption_mod
from . import scraper, state
from .gemini_video import clean_product_shot, generate_product_video
from .story_image import build_story_image
from .telegram_post import send_photo, send_video

CLEANUP_MAX_ATTEMPTS = 3


def run() -> None:
    print("Katalog taranıyor...")
    catalog = scraper.list_light_catalog()
    print(f"{len(catalog)} ürün bulundu (BOT kategorisi hariç).")

    candidate = state.pick_candidate(catalog)
    if not candidate:
        print("Uygun ürün bulunamadı, çıkılıyor.")
        return

    print(f"Seçilen ürün: {candidate['title']} -> {candidate['url']}")
    product = scraper.fetch_product(candidate["url"], category_slug=candidate.get("category_slug"))

    if not product.main_image:
        print("Ana görsel bulunamadı, bu ürün atlanıyor.")
        return

    with tempfile.TemporaryDirectory() as tmp:
        raw_image_path = scraper.download_binary(product.main_image, f"{tmp}/product_raw.jpg")

        clean_image_path = f"{tmp}/product_clean.jpg"
        image_path = raw_image_path
        for attempt in range(1, CLEANUP_MAX_ATTEMPTS + 1):
            try:
                print(f"Ürün görseli 'ayaksız' hale getiriliyor (deneme {attempt}/{CLEANUP_MAX_ATTEMPTS})...")
                clean_product_shot(raw_image_path, clean_image_path)
                image_path = clean_image_path
                break
            except Exception as exc:  # noqa: BLE001
                print(f"UYARI: görsel temizleme denemesi {attempt} başarısız: {exc}")
                if attempt == CLEANUP_MAX_ATTEMPTS:
                    print("Tüm denemeler başarısız, orijinal görselle devam ediliyor.")
                    image_path = raw_image_path

        video_path = f"{tmp}/product_video.mp4"
        story_path = f"{tmp}/story.jpg"

        print("Gemini ile video üretiliyor (birkaç dakika sürebilir)...")
        generate_product_video(image_path, video_path)

        print("Hikaye görseli oluşturuluyor...")
        build_story_image(image_path, product.title, product.price_text, story_path)

        text = caption_mod.build_caption(product.title, product.brand, product.category_slug)

        print("Telegram'a gönderiliyor...")
        send_video(video_path, text)
        send_photo(story_path, "📲 Hikayede paylaşmak için hazır görsel")

    state.mark_posted(product.url, product.title)
    print("Tamamlandı, data/posted.json güncellendi.")


if __name__ == "__main__":
    try:
        run()
    except Exception as exc:  # noqa: BLE001
        print(f"HATA: {exc}", file=sys.stderr)
        raise
