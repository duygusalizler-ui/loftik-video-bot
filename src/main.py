"""
Ana akış:

1. Kategorilerdeki ürün linklerini topla (BOT kategorisi hariç)
2. Daha önce paylaşılmamış rastgele bir ürün seç
3. Seçilen ürünün detayını çek (görsel, marka, fiyat)
4. Ana ürün görselini indir
5. Hikaye görseli için "ayaksız" bir versiyon üret (en fazla 3 deneme)
6. Wiro AI (MiniMax H3 R2V) ile dikey (9:16) ürün videosu üret -- birden
   fazla ürün görseli referans olarak gönderilir (tasarım tutarlılığı için).
   Başarısız olursa otomatik olarak Gemini (Veo) ile tekrar dener.
7. Instagram/Telegram hikayesi için dikey (temiz, ayaksız) görsel üret
8. Chekich.com.tr'de en yakın eşleşen ürünü bulup gerçek malzeme/astar/topuk
   bilgisini çek (bulamazsa uydurmadan atlar)
9. Açıklama + hashtag oluştur
10. Telegram'a video + hikaye görselini gönder
11. data/posted.json dosyasını güncelle (GitHub Actions bunu commit'ler)

Çalıştırmak için: python -m src.main
"""
import sys
import tempfile

from . import caption as caption_mod
from . import chekich, config, scraper, state
from . import wiro_video
from .gemini_video import QuotaExceededError, clean_product_shot
from .gemini_video import generate_product_video as generate_product_video_gemini
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

        # Video, BİLEREK ham (giyili) görselden başlıyor -- ilk ~1sn "kapak" gibi,
        # sonra podyuma geçiş yapıyor (bkz. gemini_video.SCENE_PROMPT).
        # Hikaye görseli (statik) için ise ayrı olarak "ayaksız" temiz görsel üretiyoruz,
        # çünkü sabit bir görselde yarım kesilmiş bacak iyi durmuyor.
        clean_image_path = f"{tmp}/product_clean.jpg"
        story_source_path = raw_image_path
        for attempt in range(1, CLEANUP_MAX_ATTEMPTS + 1):
            try:
                print(f"Hikaye görseli için 'ayaksız' versiyon üretiliyor (deneme {attempt}/{CLEANUP_MAX_ATTEMPTS})...")
                clean_product_shot(raw_image_path, clean_image_path)
                story_source_path = clean_image_path
                break
            except Exception as exc:  # noqa: BLE001
                print(f"UYARI: görsel temizleme denemesi {attempt} başarısız: {exc}")
                if attempt == CLEANUP_MAX_ATTEMPTS:
                    print("Tüm denemeler başarısız, hikaye görseli de ham fotoğraftan üretilecek.")
                    story_source_path = raw_image_path

        video_path = f"{tmp}/product_video.mp4"
        story_path = f"{tmp}/story.jpg"

        if config.VIDEO_PROVIDER == "wiro":
            print("Wiro (MiniMax H3 R2V) ile video üretiliyor (birkaç dakika sürebilir)...")
            image_urls = [product.main_image] + [
                u for u in product.gallery_images if u != product.main_image
            ]
            image_urls = image_urls[:5]  # ilk 5 gorsel ucretsiz (referans gorsel maliyeti icin)
            try:
                wiro_video.generate_product_video(image_urls, video_path)
            except Exception as exc:  # noqa: BLE001
                print(f"UYARI: Wiro basarisiz ({exc}), Gemini (Veo) ile tekrar deneniyor.")
                generate_product_video_gemini(raw_image_path, video_path)
        else:
            print("Gemini ile video üretiliyor (birkaç dakika sürebilir)...")
            generate_product_video_gemini(raw_image_path, video_path)

        print("Hikaye görseli oluşturuluyor...")
        build_story_image(story_source_path, product.title, product.price_text, story_path)

        spec_line = None
        try:
            print("Chekich'te en yakın eşleşen ürün aranıyor (gerçek malzeme/astar bilgisi için)...")
            specs = chekich.find_matching_specs(product.title)
            if specs:
                print(f"Eşleşme bulundu: {specs.matched_title} -> {specs.source_url}")
                spec_line = caption_mod.build_spec_line(specs)
            else:
                print("Yeterince iyi bir eşleşme bulunamadı, özellik satırı eklenmeyecek.")
        except Exception as exc:  # noqa: BLE001
            print(f"UYARI: Chekich eşleştirme başarısız ({exc}), özellik satırı olmadan devam ediliyor.")

        text = caption_mod.build_caption(product.title, product.brand, product.category_slug, spec_line)

        print("Telegram'a gönderiliyor...")
        send_video(video_path, text)
        send_photo(story_path, "📲 Hikayede paylaşmak için hazır görsel")

    state.mark_posted(product.url, product.title)
    print("Tamamlandı, data/posted.json güncellendi.")


if __name__ == "__main__":
    try:
        run()
    except QuotaExceededError as exc:
        # Bu bir hata degil -- Gemini kotasi (429) dolmus. Kirmizi X yerine
        # temiz, bilgilendirici bir cikis yapiyoruz; bir sonraki tetiklemede
        # kota yenilenmis olacak ve otomasyon normal calisacak.
        print(f"BİLGİ: {exc}")
        print("Bu run'i basarisiz saymiyoruz -- sadece kota doldugu icin atlaniyor.")
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        print(f"HATA: {exc}", file=sys.stderr)
        raise
