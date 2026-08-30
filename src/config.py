import os

SITE_BASE_URL = os.environ.get("SITE_BASE_URL", "https://www.loftikayakkabi.com")

# Otomasyonun tarayacağı kategori sayfaları.
# Yeni bir kategori eklemek/çıkarmak istersen buradan düzenle.
CATEGORY_URLS = [
    f"{SITE_BASE_URL}/kategori/spor-ayakkabi",
    f"{SITE_BASE_URL}/kategori/erkek-ayakkabi",
    f"{SITE_BASE_URL}/kategori/kadin-ayakkabi",
    f"{SITE_BASE_URL}/kategori/deri-ayakkabi",
]

# Bu kategori slug'larındaki ürünler otomasyona HİÇ girmez.
# "bot" = BOT (kışlık bot ayakkabı) kategorisi -> yazın anlamsız olduğu için hariç.
# Kış gelince tekrar dahil etmek istersen bu setten çıkarman yeterli.
EXCLUDED_CATEGORY_SLUGS = {"bot"}

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
WIRO_API_KEY = os.environ.get("WIRO_API_KEY")

# Video uretimi icin hangi saglayici kullanilsin: "wiro" veya "gemini"
VIDEO_PROVIDER = os.environ.get("VIDEO_PROVIDER", "wiro")

# "post"  -> AI video YOK, sadece sitedeki GERCEK fotograf + marka sablonu
#            (hallucination riski sifir -- toka/logo/desen degismez cunku
#            hicbir AI video/gorsel duzenleme adimi calismiyor)
# "video" -> eski akis: AI ile giyili-kapak + donen podyum videosu uretir
CONTENT_MODE = os.environ.get("CONTENT_MODE", "post")

# Bu API anahtari icin ListModels ile dogrulandi: sadece Veo 3.1 preview
# modelleri destekleniyor (veo-2.0 / veo-3.0 bu anahtarda YOK). "fast" varyanti
# hem daha ucuz hem daha hizli uretiyor -- gunde 4-5 video icin mantikli secim.
# Daha kaliteli ama daha pahali/yavas istersen: veo-3.1-generate-preview
VIDEO_MODEL = os.environ.get("VEO_MODEL", "veo-3.1-fast-generate-preview")
VIDEO_ASPECT_RATIO = "9:16"

STATE_FILE = "data/posted.json"
BRAND_NAME = "Loftik Ayakkabı"
BRAND_HASHTAG = "#loftikayakkabi"
