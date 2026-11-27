"""Edge TTS (ücretsiz) ile sahne sahne anlatım sesi üretir."""
from __future__ import annotations

import asyncio
import os
import ssl
import subprocess

import edge_tts
import edge_tts.communicate as _comm

from . import config as C

# edge-tts kendi certifi bağlamını kullanır; kurumsal proxy/CA arkasında
# SSL_CERT_FILE verilmişse onu kullan (GitHub Actions'ta gerek yok).
if os.environ.get("SSL_CERT_FILE"):
    _comm._SSL_CTX = ssl.create_default_context(cafile=os.environ["SSL_CERT_FILE"])


def duration(path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


async def _say(text: str, out, voice: str, rate: str) -> None:
    for attempt in range(3):
        try:
            await edge_tts.Communicate(text, voice, rate=rate).save(str(out))
            return
        except Exception:
            if attempt == 2:
                raise
            await asyncio.sleep(2 * (attempt + 1))


def narrate(ep: dict, voice: str = C.VOICE_EN, rate: str = C.VOICE_RATE, lang: str = "en") -> dict:
    """Her sahne için mp3 üretir (varsa atlar). {n: süre_sn} döner."""
    out_dir = C.BUILD_DIR / ep["id"] / f"audio_{lang}"
    out_dir.mkdir(parents=True, exist_ok=True)
    durations = {}
    for s in ep["scenes"]:
        text = s["narration"] if lang == "en" else s[f"narration_{lang}"]
        mp3 = out_dir / f"{s['n']:03d}.mp3"
        if not mp3.exists() or mp3.stat().st_size == 0:
            asyncio.run(_say(text, mp3, voice, rate))
        durations[s["n"]] = duration(mp3)
    return durations
