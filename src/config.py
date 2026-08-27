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

# Google'ın "Veo 2" modeli hem 16:9 hem 9:16 (dikey) görsel-den-videoyu
# resmi olarak destekliyor (Ağustos 2026 itibarıyla). Veo 3 bazı arayüzlerde
# görsel referanslı üretimde henüz sadece 16:9 destekliyor olabilir; sorun
# yaşarsan güncel duruma https://ai.google.dev/gemini-api/docs/video adresinden bak.
VIDEO_MODEL = os.environ.get("VEO_MODEL", "veo-2.0-generate-001")
VIDEO_ASPECT_RATIO = "9:16"

STATE_FILE = "data/posted.json"
BRAND_NAME = "Loftik Ayakkabı"
BRAND_HASHTAG = "#loftikayakkabi"
