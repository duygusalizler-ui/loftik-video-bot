import os


def _list(name: str, default: str) -> list[str]:
    return [m.strip() for m in (os.environ.get(name) or default).split(",") if m.strip()]


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
TEXT_MODELS = _list("STORYADS_TEXT_MODELS", "gemini-3.8-flash,gemini-3-flash,gemini-2.5-flash")
IMAGE_MODELS = _list("STORYADS_IMAGE_MODELS", "gemini-3-pro-image,gemini-2.5-flash-image")
VIDEO_MODEL = os.environ.get("STORYADS_VIDEO_MODEL") or os.environ.get("VEO_MODEL") or "veo-3.1-fast-generate-preview"
CLIP_SECONDS = int(os.environ.get("STORYADS_CLIP_SECONDS", "6"))

SCENES = int(os.environ.get("STORYADS_SCENES", "5"))           # 5 sahne ~ 22-28 sn
QA_MIN = int(os.environ.get("STORYADS_QA_MIN", "7"))            # 10 uzerinden
IMAGE_TRIES = int(os.environ.get("STORYADS_IMAGE_TRIES", "3"))
CLIP_TRIES = int(os.environ.get("STORYADS_CLIP_TRIES", "2"))
MUSIC_VOLUME = float(os.environ.get("STORYADS_MUSIC_VOLUME", "0.22"))
HISTORY_FILE = os.environ.get("STORYADS_HISTORY", "data/storyads_gecmis.json")
