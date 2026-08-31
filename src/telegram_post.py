"""Telegram Bot API ile video ve fotoğraf paylaşımı."""
import json

import requests

from . import config

API_BASE = "https://api.telegram.org/bot{token}/{method}"


def _url(method: str) -> str:
    if not config.TELEGRAM_BOT_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN tanımlı değil (GitHub Secrets'a eklemeyi unutma).")
    return API_BASE.format(token=config.TELEGRAM_BOT_TOKEN, method=method)


def _chat_id() -> str:
    if not config.TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_CHAT_ID tanımlı değil (GitHub Secrets'a eklemeyi unutma).")
    return config.TELEGRAM_CHAT_ID


def send_video(video_path: str, caption: str) -> dict:
    with open(video_path, "rb") as f:
        resp = requests.post(
            _url("sendVideo"),
            data={"chat_id": _chat_id(), "caption": caption, "supports_streaming": True},
            files={"video": f},
            timeout=180,
        )
    resp.raise_for_status()
    return resp.json()


def send_photo(photo_path: str, caption: str = "") -> dict:
    with open(photo_path, "rb") as f:
        resp = requests.post(
            _url("sendPhoto"),
            data={"chat_id": _chat_id(), "caption": caption},
            files={"photo": f},
            timeout=60,
        )
    resp.raise_for_status()
    return resp.json()


def send_media_group(photo_paths: list, caption: str = "") -> dict:
    """
    Birden fazla fotoğrafı TEK bir "kaydırmalı" (carousel) gönderi olarak
    yollar -- Instagram'daki çoklu-görsel gönderiye karşılık gelir.
    Telegram en az 2 medya gerektirir; tek görsel varsa send_photo kullan.
    """
    if len(photo_paths) < 2:
        raise ValueError("send_media_group en az 2 fotoğraf gerektirir; tek görsel için send_photo kullan.")

    media = []
    files = {}
    open_files = []
    try:
        for i, path in enumerate(photo_paths):
            key = f"photo{i}"
            item = {"type": "photo", "media": f"attach://{key}"}
            if i == 0 and caption:
                item["caption"] = caption
            media.append(item)
            f = open(path, "rb")
            open_files.append(f)
            files[key] = f

        resp = requests.post(
            _url("sendMediaGroup"),
            data={"chat_id": _chat_id(), "media": json.dumps(media)},
            files=files,
            timeout=180,
        )
        resp.raise_for_status()
        return resp.json()
    finally:
        for f in open_files:
            f.close()
