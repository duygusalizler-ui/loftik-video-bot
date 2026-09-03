"""
Wiro AI uzerinden KlingAI v2.1-master modeliyle urun videosu uretir.

NEDEN KLING: 2026 karsilastirmalarinda Kling, "referans goruntuye sadakat"
konusunda one cikan model -- Veo/Sora gibi modeller referansi "yaratici"
sekilde yeniden yorumlayabiliyor (bizim yasadigimiz sahte logo/desen
sorunlarinin sebebi), Kling ise verilen goruntuyu cok daha sadik koruyor.
Ayrica metin/yazi tutarliliginda da lider (bizim "yazi bozulmasi"
sorunumuzu da azaltmasi beklenir).

API akisi (asenkron):
1) POST /v1/Run/klingai/image-to-video-klingai-v2.1-master -> taskid doner
2) POST /v1/Task/Detail (taskid ile) -> tamamlanana kadar sorgula
3) pexit == "0" ise outputs[0]['url'] gercek video CDN linkidir, indir

Parametreler (Wiro'nun kendi model sayfasindan dogrulandi):
- prompt: metin talimati
- negativePrompt: istenmeyen seyler (opsiyonel)
- inputImageFirst: baslangic karesi olacak goruntunun URL'si
- videoSeconds: 5 veya 10
"""
from __future__ import annotations

import time

import requests

from . import config

BASE_URL = "https://api.wiro.ai/v1"
MODEL_PATH = "klingai/image-to-video-klingai-v2.1-master"

PROMPT_TEMPLATE = (
    "This is authentic, candid, unpolished content -- like something "
    "filmed casually on a phone by a regular person, NOT a polished "
    "studio advertisement. The reference image shows a pair of shoes worn "
    "on a person's feet while walking outdoors. Continue this exact scene "
    "naturally: the person keeps walking at a relaxed, everyday pace "
    "along the same street/path. The camera follows at a low angle "
    "(roughly ankle to knee height), with a natural handheld feel -- a "
    "little natural camera wobble/shake is good and expected, do not "
    "smooth it into a stabilized cinematic shot. Real daylight, real "
    "outdoor environment, genuine and casual the whole time. ABSOLUTELY "
    "NO studio lighting, NO rotating display podium, NO product-showcase "
    "staging, NO dramatic camera moves, NO scene cuts or transitions of "
    "any kind -- one continuous, unedited-looking shot from start to "
    "end, same camera style, same location throughout, the person and "
    "their legs stay visible the entire time exactly as in the "
    "reference. "
    "CRITICAL: keep the shoe design, colors, materials, graphic "
    "patterns, hardware, buckles, clasps, and any text or logos EXACTLY "
    "identical to the reference image throughout -- do not alter, "
    "redesign, simplify, or invent any new pattern, logo, buckle shape, "
    "or brand text anywhere on the shoes. If a part of the shoe is "
    "plain/blank in the reference, keep it plain and blank. Every small "
    "detail (stitching, heel shape, sole texture and color, toe shape, "
    "laces, decorative elements) must survive unchanged -- when unsure, "
    "copy it directly from the reference rather than guessing."
)

NEGATIVE_PROMPT = (
    "studio lighting, rotating podium, product display stand, scene cut, "
    "transition, logo change, new logo, changed pattern, changed buckle "
    "shape, changed color, blurry text, distorted shoe, extra limbs, "
    "watermark"
)


def _headers() -> dict:
    if not config.WIRO_API_KEY:
        raise RuntimeError("WIRO_API_KEY tanımlı değil (GitHub Secrets'a eklemeyi unutma).")
    return {"x-api-key": config.WIRO_API_KEY, "Content-Type": "application/json"}


def _start_run(image_url: str) -> str:
    payload = {
        "prompt": PROMPT_TEMPLATE,
        "negativePrompt": NEGATIVE_PROMPT,
        "inputImageFirst": image_url,
        "videoSeconds": 5,
    }
    resp = requests.post(f"{BASE_URL}/Run/{MODEL_PATH}", headers=_headers(), json=payload, timeout=30)
    data = resp.json()
    if not data.get("result"):
        raise RuntimeError(f"Wiro (Kling) run baslatilamadi: {data.get('errors')}")
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
    """image_urls: en az 1 gorsel URL'si -- sadece ilki (ana/giyili foto) kullanilir."""
    taskid = _start_run(image_urls[0])
    video_url = _poll_task(taskid)
    return _download(video_url, output_path)
