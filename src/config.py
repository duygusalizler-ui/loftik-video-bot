import os

SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://www.loftikayakkabi.com")

# Otomasyonun tarayacağı kategori sayfaları.
# Yeni bir kategori eklemek/çıkarmak istersen buradan düzenle.
CATEGORY_URLS = [
    f"{SITE_BASE_URL}/kategori/spor-ayakkabi",
    f"{SITE_BASE_URL}/kategori/erkek-ayakkabi",
    f"{SITE_BASE_URL}/kategori/kadin-ayakkabi",
    f"{SITE_BASE_URL}/kategori/deri-ayakkabi",
    f"{SITE_BASE_URL}/kategori/bot",
]

# BOT sezonu: bu aylarda botlar otomasyona girer, diger aylarda (yaz) otomatik
# olarak hariç tutulur. Elle zorlamak icin BOT_MODE=on / off kullan.
BOT_SEASON_MONTHS = {9, 10, 11, 12, 1, 2, 3}
BOT_MODE = os.environ.get("BOT_MODE", "auto").lower()  # auto | on | off


def boots_enabled(month: int | None = None) -> bool:
    if BOT_MODE == "on":
        return True
    if BOT_MODE == "off":
        return False
    if month is None:
        from datetime import datetime, timezone, timedelta

        month = datetime.now(timezone(timedelta(hours=3))).month  # TR saati
    return month in BOT_SEASON_MONTHS


# Bot sezonunda botlara oncelik verilir: adaylarin bu orani bot olur.
BOT_PRIORITY_IN_SEASON = float(os.environ.get("BOT_PRIORITY_IN_SEASON", "0.7"))

# Bu kategori slug'larındaki ürünler otomasyona HİÇ girmez.
# "bot" artik burada degil -- sezona gore boots_enabled() karar veriyor.
EXCLUDED_CATEGORY_SLUGS = set(
    s.strip() for s in os.environ.get("EXCLUDED_CATEGORY_SLUGS", "").split(",") if s.strip()
)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
WIRO_API_KEY = os.environ.get("WIRO_API_KEY")

# Video uretimi icin hangi saglayici kullanilsin: "wiro" veya "gemini"
VIDEO_PROVIDER = os.environ.get("VIDEO_PROVIDER", "wiro")

# "video"    -> Wiro (MiniMax H3 R2V) / Gemini (Veo) ile ham/otantik (UGC
#               tarzi) video uretir -- kisi ayakkabiyla dogal yuruyor gibi,
#               podyum degil (varsayilan -- viral/paylasim performansi icin
#               otantik format daha etkili)
# "remotion" -> AI YOK, kod (Remotion/React) ile GERCEK fotograflari
#               donen bir podyum sahnesine yerlestirir. Hallucination
#               riski sifir ama daha "reklam gibi" durur.
# "post"     -> AI YOK, gercek fotograflari oldugu gibi kaydirmali gonderi
#               olarak yollar (video render'a gerek yoksa)
# "reklam"   -> (VARSAYILAN) rakip reklam analizi + sahne gorseli + AI video
#               + otomatik kalite kontrolu + Turkce yazili kurgu. Bkz. src/ad_pipeline.py
CONTENT_MODE = (os.environ.get("CONTENT_MODE") or "reklam").strip().lower()

# Bu API anahtari icin ListModels ile dogrulandi: sadece Veo 3.1 preview
# modelleri destekleniyor (veo-2.0 / veo-3.0 bu anahtarda YOK). "fast" varyanti
# hem daha ucuz hem daha hizli uretiyor -- gunde 4-5 video icin mantikli secim.
# Daha kaliteli ama daha pahali/yavas istersen: veo-3.1-generate-preview
VIDEO_MODEL = os.environ.get("VEO_MODEL", "veo-3.1-fast-generate-preview")
VIDEO_ASPECT_RATIO = "9:16"

STATE_FILE = "data/posted.json"
BRAND_NAME = "Loftik Ayakkabı"
BRAND_HASHTAG = "#loftikayakkabi"

# ---------------------------------------------------------------------------
# "reklam" modu ayarlari
# ---------------------------------------------------------------------------
APIFY_TOKEN = os.environ.get("APIFY_TOKEN")
# Meta Ad Library'yi tarayan Apify actor'u. Degistirmek istersen buradan.
APIFY_ADS_ACTOR = os.environ.get("APIFY_ADS_ACTOR", "apify~facebook-ads-scraper")
AD_LIBRARY_COUNTRY = os.environ.get("AD_LIBRARY_COUNTRY", "TR")
# Her anahtar kelime icin kac reklam cekilsin
COMPETITOR_ADS_PER_KEYWORD = int(os.environ.get("COMPETITOR_ADS_PER_KEYWORD", "15"))
# Takip edilen rakip marka/sayfa adlari (virgulle). Bos olabilir.
COMPETITOR_PAGES = [
    s.strip() for s in os.environ.get("COMPETITOR_PAGES", "").split(",") if s.strip()
]

# Gemini modelleri (repoda calistigi dogrulanmis olanlar varsayilan)
GEMINI_TEXT_MODEL = os.environ.get("GEMINI_TEXT_MODEL") or "gemini-3.8-flash"
# Ana model kapanirsa sirayla denenecek yedekler (404 alinca otomatik gecer)
GEMINI_TEXT_FALLBACKS = [
    m.strip()
    for m in (os.environ.get("GEMINI_TEXT_FALLBACKS") or "gemini-3.8-flash,gemini-3-flash,gemini-2.5-flash").split(",")
    if m.strip()
]
GEMINI_IMAGE_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-2.5-flash-image")

# Reklam videosu kac sahneden olussun (her sahne ~8 sn Veo klibi).
# 2 sahne = ~16 sn video.
AD_SCENES = int(os.environ.get("AD_SCENES", "2"))
# Kalite kontrolu: 10 uzerinden bu puanin altindaki gorsel/klip atilir.
QA_MIN_SCORE = int(os.environ.get("QA_MIN_SCORE") or "7")
SCENE_IMAGE_ATTEMPTS = int(os.environ.get("SCENE_IMAGE_ATTEMPTS", "3"))
CLIP_ATTEMPTS = int(os.environ.get("CLIP_ATTEMPTS", "2"))

# Gunde en fazla kac icerik uretilsin (hem cron-job.org hem GitHub
# schedule tetiklese bile bu sayi asilmaz).
MAX_POSTS_PER_DAY = int(os.environ.get("MAX_POSTS_PER_DAY") or "2")
# Elle deneme calistirmalarinda gunluk limiti atlamak icin (workflow input'u)
IGNORE_DAILY_LIMIT = (os.environ.get("IGNORE_DAILY_LIMIT") or "").lower() in ("1", "true", "evet")

COMPETITOR_REPORT_DIR = "data/rakip_raporlari"
