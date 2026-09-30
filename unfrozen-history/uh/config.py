"""Unfrozen History — sabit ayarlar ve bütçe kuralları."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EPISODES_DIR = ROOT / "episodes"
DATA_DIR = ROOT / "data"
LEDGER_PATH = DATA_DIR / "ledger.json"
USED_TOPICS_PATH = DATA_DIR / "used_topics.json"  # tekrar engeli
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
    "generate_audio": True,  # ortam sesi (ateş, rüzgâr, kar) — fiyat aynı, get_cost ile doğrulandı
    "aspect_ratio": "16:9",
}
CLIP_COST = 7.5  # 0.5 kredi/sn x 15 sn (sesli/sessiz aynı)

# --- Görsel stil (her sahne promptuna eklenir) ---
STYLE = (
    "Hand-painted gouache and watercolor storybook illustration, visible brush "
    "texture, warm amber firelight against cold blue winter light, cinematic "
    "composition, historically accurate early 14th-century English peasant "
    "material culture: no chimneys (smoke escapes through the thatch), no glass in "
    "windows (small openings with wooden shutters), soft painterly detail, no text, "
    "no letters, no watermark"
)
# Referans kartları (karakter/mekân) — her bölümde önce bunlar üretilir
REF_STYLE = (
    "Hand-painted gouache and watercolor storybook character/location reference "
    "sheet, same painterly look as the episode, even neutral lighting, plain warm "
    "parchment background, historically accurate early 14th-century English "
    "peasant clothing, original fictional person, no text, no labels, no watermark"
)
REF_LEAD = (
    "Use the attached reference images only to keep the same characters "
    "(faces, hair, clothing) and the same places consistent; compose a new scene:"
)
POV_HINT = (
    "First-person point of view: we see through the narrator's own eyes, "
    "his rough work-worn hands and wool sleeves may be visible in the foreground"
)
MOTION_SUFFIX = (
    "Gentle natural motion, soft cuts between shots, painterly style and "
    "characters stay consistent across shots, no text"
)
SOUND_SUFFIX = "Natural ambient sound effects only; no speech, no voices talking, no music"

# --- Ses ---
VOICE_EN = "en-US-ChristopherNeural"
VOICE_RATE = "-5%"
VOICE_DE = "de-DE-ConradNeural"  # ileride ikinci ses kanalı
# Kanal sahibinin klon sesi (Higgsfield, Qwen TTS ~0,11 kredi/sahne). Klon bir kerelik 40 kredi.
CLONE_VOICE_ID = "07112420-b262-46e4-8698-6d2a177958f4"
CLONE_TTS = {"model": "qwen_audio_tts", "voice_type": "element", "voice_id": CLONE_VOICE_ID,
             "language": "en", "format": "mp3", "sample_rate": 44100, "speech_rate": 1.1,
             "instruction": "Calm, low, warm storyteller by the fire; steady pace, short natural pauses; clear native English."}

# --- Montaj ---
OUT_W, OUT_H, OUT_FPS = 1920, 1080, 30
MIN_SPEED = 0.65  # sakin klipler en fazla bu kadar yavaşlatılır (15 sn -> ~23 sn)
BEAT_PAD = 0.35   # her cümle bloğu sonrası nefes payı (sn)
MUSIC_DB = -24    # müzik, anlatımın altında
MUSIC_BED_DB = -9  # bölüm müzik yatağı (-20 LUFS'e normalize) — ducking ile anlatım altında kalır
MUSIC_DIR = ROOT / "build" / "music"  # telifsiz parçalar (Kevin MacLeod, CC BY 4.0) — gitignore
RENDER_WORKERS = 3  # paralel sahne render
AMBIENCE_DB = -14  # klip ortam sesi (ASMR katmanı), anlatımın altında
