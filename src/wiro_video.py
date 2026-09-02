"""
Wiro AI uzerinden MiniMax H3 R2V modeliyle urun videosu uretir.

Bu model ozellikle "urunun tasarimini birebir koru, kamera/sahne hareketi
ekle" isine odaklanmis (Veo'da yasadigimiz sahte logo / desen degisimi
sorunlarini cozmesi beklenir). Ayrica birden fazla referans goruntu kabul
ediyor (biz burada urunun ana + varsa galeri gorsellerini gonderiyoruz).

API akisi (asenkron):
1) POST /v1/Run/MiniMax/h3-r2v -> taskid doner
2) POST /v1/Task/Detail (taskid ile) -> tamamlanana kadar sorgula
3) pexit == "0" ise outputs[0]['url'] gercek video CDN linkidir, indir

NOT: Bu kod, Wiro'nun genel API dokumantasyonuna gore yazildi (Agustos
2026). inputImage parametresinin JSON'da birden fazla URL icin tam olarak
liste mi yoksa baska bir format mi bekledigi %100 dogrulanamadi (Wiro'nun
kendi playground'u dosya yukleme odakli, ben sadece dokumani okuyabildim).
Bu yuzden once liste ile deneyip, basarisiz olursa tek goruntuyle (ilk
gorsel) otomatik tekrar deniyor -- boylece yanlis format tum otomasyonu
kirmiyor.
"""
from __future__ import annotations

import time

import requests

from . import config

BASE_URL = "https://api.wiro.ai/v1"

PROMPT_TEMPLATE = (
    "The reference images show the exact same pair of shoes worn on a "
    "person's feet while walking outdoors -- this is authentic, candid, "
    "unpolished content, like something filmed casually on a phone by a "
    "regular person, NOT a polished studio advertisement. Continue this "
    "exact scene naturally: the person keeps walking at a relaxed, "
    "everyday pace along the same street/path. The camera follows at a "
    "low angle (roughly ankle to knee height), with a natural handheld "
    "feel -- a little natural camera wobble/shake is good and expected, "
    "do not smooth it into a stabilized cinematic shot. Real daylight, "
    "real outdoor environment, genuine and casual the whole time. "
    "ABSOLUTELY NO studio lighting, NO rotating display podium, NO "
    "product-showcase staging, NO dramatic camera moves, NO scene cuts "
    "or transitions of any kind -- this must stay one continuous, "
    "unedited-looking shot from start to end, same camera style, same "
    "location throughout. "
    "Keep the shoe design, colors, materials, graphic patterns, "
    "hardware, buckles, clasps, and metal fittings EXACTLY identical to "
    "the reference images throughout the entire video -- do not alter, "
    "redesign, simplify, resize, or reshape any buckle, clasp, or metal "
    "hardware (for example, if the reference shows a D-shaped or "
    "oval-shaped buckle, it must stay that exact same shape -- do not "
    "turn it into an H-shaped, rectangular, or any other differently "
    "shaped buckle or clasp). Also do not invent any new pattern, logo, "
    "or brand text anywhere on the shoes. If a part of the shoe is "
    "plain/blank in the references, keep it plain and blank. "
    "TREAT THIS AS A PRODUCT-ACCURACY TASK, NOT A CREATIVE REDESIGN: every "
    "small visual detail from the reference images must survive unchanged "
    "-- stitching lines and their exact placement, heel shape and height, "
    "sole thickness and texture, toe shape, strap width and where straps "
    "attach, eyelets and lace pattern if present, any decorative elements "
    "(bows, studs, embellishments) and their exact position, and the "
    "precise shade of every color used. When unsure about a small detail, "
    "copy it directly from the closest reference image rather than "
    "guessing or simplifying it. "
    "Vertical mobile-first framing, natural everyday clothing and "
    "surroundings exactly as in the reference, no added text, no added "
    "logos or overlays baked into the video itself."
)


def _headers() -> dict:
    if not config.WIRO_API_KEY:
        raise RuntimeError("WIRO_API_KEY tanımlı değil (GitHub Secrets'a eklemeyi unutma).")
    return {"x-api-key": config.WIRO_API_KEY, "Content-Type": "application/json"}


def _start_run(image_urls: list) -> str:
    payload = {
        "prompt": PROMPT_TEMPLATE,
        "inputImage": image_urls if len(image_urls) > 1 else image_urls[0],
        "duration": 8,
        "resolution": "768P",
        "aspectRatio": "9:16",
    }
    resp = requests.post(
        f"{BASE_URL}/Run/MiniMax/h3-r2v", headers=_headers(), json=payload, timeout=30
    )
    data = resp.json()
    if not data.get("result"):
        raise RuntimeError(f"Wiro run baslatilamadi: {data.get('errors')}")
    return data["taskid"]


def _poll_task(taskid: str, max_wait_seconds: int = 480) -> str:
    """Video tamamlanana kadar bekler, CDN video URL'sini doner."""
    waited = 0
    interval = 10
    while waited < max_wait_seconds:
        resp = requests.post(
            f"{BASE_URL}/Task/Detail", headers=_headers(), json={"taskid": taskid}, timeout=30
        )
        data = resp.json()
        if not data.get("result") or not data.get("tasklist"):
            raise RuntimeError(f"Wiro task sorgusu basarisiz: {data.get('errors')}")

        task = data["tasklist"][0]
        status = task.get("status")

        if status == "task_postprocess_end":
            if task.get("pexit") != "0":
                raise RuntimeError(f"Wiro video uretimi basarisiz (pexit={task.get('pexit')}): {task.get('debugerror')}")
            outputs = task.get("outputs") or []
            if not outputs:
                raise RuntimeError("Wiro video uretimi bitti ama cikti bulunamadi.")
            return outputs[0]["url"]

        if status == "task_cancel":
            raise RuntimeError("Wiro gorevi iptal edildi.")

        time.sleep(interval)
        waited += interval

    raise RuntimeError(f"Wiro video uretimi {max_wait_seconds}sn icinde tamamlanmadi (zaman asimi).")


def _download(url: str, dest_path: str) -> str:
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()
    with open(dest_path, "wb") as f:
        f.write(resp.content)
    return dest_path


def generate_product_video(image_urls: list, output_path: str) -> str:
    """
    image_urls: en az 1, en fazla ~9 gorsel URL'si (ilk gorsel = ana/giyili foto).
    Basit URL listesi formatinda calismazsa, otomatik olarak sadece ilk
    gorselle (tek gorsel) tekrar dener.
    """
    try:
        taskid = _start_run(image_urls)
    except Exception as exc:  # noqa: BLE001
        if len(image_urls) > 1:
            print(f"UYARI: coklu gorsel formati basarisiz ({exc}), tek gorselle tekrar deneniyor.")
            taskid = _start_run([image_urls[0]])
        else:
            raise

    video_url = _poll_task(taskid)
    return _download(video_url, output_path)
