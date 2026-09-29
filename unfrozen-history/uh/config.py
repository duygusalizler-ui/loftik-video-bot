"""Unfrozen History — sabit ayarlar ve bütçe kuralları."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPISODES_DIR = ROOT / "episodes"
DATA_DIR = ROOT / "data"
LEDGER_PATH = DATA_DIR / "ledger.json"
BUILD_DIR = ROOT / "build"  # gitignore'da; indirilen klipler, ses, render

# --- Bütçe (kredi) — kod seviyesinde sert sınırlar ---
MAX_CREDITS_PER_VIDEO = 300
MAX_CREDITS_PER_MONTH = 1200
MIN_BALANCE_RESERVE = 500  # Sunny için ayrılan rezerv; altına inilirse başlama
MAX_RETRIES_PER_ASSET = 1

# --- Higgsfield modelleri (maliyetler get_cost ile doğrulandı) ---
IMAGE_MODEL = "gpt_image_2"
IMAGE_PARAMS = {"quality": "medium", "resolution": "1k", "aspect_ratio": "16:9"}
IMAGE_COST = 1.0

VIDEO_MODEL = "seedance_2_0_mini"
CLIP_SECONDS = 15
VIDEO_PARAMS = {
    "duration": CLIP_SECONDS,
    "resolution": "480p",
    "generate_audio": False,
    "aspect_ratio": "16:9",
}
CLIP_COST = 7.5  # 0.5 kredi/sn x 15 sn

# --- Görsel stil (her sahne promptuna eklenir) ---
STYLE = (
    "Hand-painted gouache and watercolor storybook illustration, visible brush "
    "texture, warm amber firelight against cold blue winter light, cinematic "
    "composition, historically accurate early 14th-century English peasant "
    "material culture, soft painterly detail, no text, no letters, no watermark"
)
POV_HINT = (
    "First-person point of view: we see through the narrator's own eyes, "
    "his rough work-worn hands and wool sleeves may be visible in the foreground"
)
MOTION_SUFFIX = (
    "Slow, gentle, natural motion; subtle camera drift; painterly style stays "
    "consistent; no text; no sudden cuts"
)

# --- Ses ---
VOICE_EN = "en-US-ChristopherNeural"
VOICE_RATE = "-5%"
VOICE_DE = "de-DE-ConradNeural"  # ileride ikinci ses kanalı

# --- Montaj ---
OUT_W, OUT_H, OUT_FPS = 1920, 1080, 30
MIN_SPEED = 0.65  # sakin klipler en fazla bu kadar yavaşlatılır (15 sn -> ~23 sn)
BEAT_PAD = 0.35   # her cümle bloğu sonrası nefes payı (sn)
MUSIC_DB = -24    # müzik, anlatımın altında
