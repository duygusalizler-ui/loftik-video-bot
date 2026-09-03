"""
Ana akış:

1. Kategorilerdeki ürün linklerini topla (BOT kategorisi hariç)
2. Daha önce paylaşılmamış rastgele bir ürün seç
3. Seçilen ürünün detayını çek (görsel, marka, fiyat)
4. Ana ürün görselini ve galerideki diğer gerçek fotoğrafları indir
5. Chekich.com.tr'de en yakın eşleşen ürünü bulup gerçek malzeme/astar/topuk
   bilgisini çek (bulamazsa uydurmadan atlar), açıklama + hashtag oluştur

CONTENT_MODE = "remotion" (varsayılan) ise:
6a. Bacak/ayak kaldırılır (AI, ama SADECE bu tek iş için -- ürünü yeniden
    çizmiyor, sadece etrafındaki bacağı siliyor; en fazla 3 deneme)
6b. Arka plan kaldırılır (rembg -- AI DEĞİL, sadece segmentasyon/kesme)
6c. Remotion (kod ile video oluşturan sistem), bu temiz kesimi kod ile
    çizilmiş dönen bir podyumun üzerine yerleştirip videoya çevirir.
    Render başarısız olursa gerçek fotoğrafları kaydırmalı gönderi
    olarak yollar.

CONTENT_MODE = "post" ise:
6b. AI YOK -- gerçek fotoğrafları olduğu gibi kaydırmalı (carousel) gönderi
    olarak yollar (video render'a gerek yoksa).

CONTENT_MODE = "video" ise (eski akış):
6c. Wiro AI (MiniMax H3 R2V) / Gemini (Veo) ile AI video üretir (giyili
    kapak + dönen podyum).

7. data/posted.json dosyasını güncelle (GitHub Actions bunu commit'ler)

Çalıştırmak için: python -m src.main
"""
import sys
import tempfile

from . import caption as caption_mod
from . import chekich, config, remotion_video, scraper, state
from . import wiro_video
from .gemini_video import QuotaExceededError, clean_product_shot
from .gemini_video import generate_product_video as generate_product_video_gemini
from .story_image import build_story_image
from .telegram_post import send_media_group, send_photo, send_video

CLEANUP_MAX_ATTEMPTS = 3


def _download_gallery(product, raw_image_path: str, tmp: str) -> list:
    gallery_urls = [product.main_image] + [
        u for u in product.gallery_images if u != product.main_image
    ]
    gallery_urls = gallery_urls[:10]

    local_paths = [raw_image_path]  # ana gorsel zaten indirildi
    for i, url in enumerate(gallery_urls[1:], start=1):
        try:
            p = scraper.download_binary(url, f"{tmp}/gallery_{i}.jpg")
            local_paths.append(p)
        except Exception as exc:  # noqa: BLE001
            print(f"UYARI: galeri görseli indirilemedi ({url}): {exc}")
    return local_paths


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

        if config.CONTENT_MODE in ("remotion", "post"):
            local_paths = _download_gallery(product, raw_image_path, tmp)

            if config.CONTENT_MODE == "remotion":
                video_path = f"{tmp}/product_video.mp4"

                # 1) Bacagi/ayagi kaldir (AI, ama SADECE bu tek is icin --
                #    urunun kendisini "yeniden cizmiyor", sadece etrafindaki
                #    bacagi siliyor). En fazla 3 deneme.
                leg_free_path = raw_image_path
                for attempt in range(1, CLEANUP_MAX_ATTEMPTS + 1):
                    try:
                        print(f"Bacak/ayak kaldırılıyor (deneme {attempt}/{CLEANUP_MAX_ATTEMPTS})...")
                        candidate_path = f"{tmp}/product_legfree.jpg"
                        clean_product_shot(raw_image_path, candidate_path)
                        leg_free_path = candidate_path
                        break
                    except Exception as exc:  # noqa: BLE001
                        print(f"UYARI: bacak kaldırma denemesi {attempt} başarısız: {exc}")
                        if attempt == CLEANUP_MAX_ATTEMPTS:
                            print("Tüm denemeler başarısız, orijinal (giyili) fotoğrafla devam ediliyor.")

                # 2) Arka planı kaldır (rembg, AI DEĞİL -- sadece segmentasyon).
                podium_paths = [leg_free_path]
                try:
                    from . import background_removal  # lazy import (bkz. background_removal.py notu)

                    print("Ürün arka planı kaldırılıyor (rembg, AI değil -- segmentasyon)...")
                    cutout_path = f"{tmp}/product_cutout.png"
                    background_removal.remove_background(leg_free_path, cutout_path)
                    podium_paths = [cutout_path]
                except Exception as exc:  # noqa: BLE001
                    print(f"UYARI: arka plan kaldırma başarısız ({exc}), bacaksız fotoğrafla devam ediliyor.")

                print("Remotion ile video üretiliyor (podyum sahnesi)...")
                try:
                    remotion_video.generate_product_video(
                        podium_paths, product.title, product.brand, product.price_text, video_path
                    )
                    print("Telegram'a gönderiliyor...")
                    send_video(video_path, text)
                except Exception as exc:  # noqa: BLE001
                    print(f"UYARI: Remotion render başarısız ({exc}), gerçek fotoğraflar kaydırmalı gönderi olarak yollanıyor.")
                    if len(local_paths) >= 2:
                        send_media_group(local_paths, text)
                    else:
                        send_photo(local_paths[0], text)
            else:
                print(f"{len(local_paths)} gerçek ürün fotoğrafı Telegram'a (kaydırmalı) gönderiliyor...")
                if len(local_paths) >= 2:
                    send_media_group(local_paths, text)
                else:
                    send_photo(local_paths[0], text)

        else:
            # Eski akis: AI video (Wiro/Gemini) + hikaye gorseli.
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
                image_urls = image_urls[:5]  # ilk 5 gorsel ucretsiz
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
