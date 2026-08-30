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
    "The reference images show the exact same pair of shoes -- Image 1 is "
    "the shoes worn on a person's feet (on-foot reference), the remaining "
    "images are close-up product-only reference angles of the exact same "
    "shoes. Keep the shoe design, colors, materials, graphic patterns, "
    "and any text or logos on the shoes EXACTLY identical to the "
    "reference images throughout the entire video -- do not alter, "
    "redesign, simplify, or invent any new pattern, logo, or brand text "
    "anywhere on the shoes. If a part of the shoe is plain/blank in the "
    "references, keep it plain and blank. "
    "The video opens on a completely static held frame matching Image 1 "
    "(the on-foot shot) for about 1 second -- no camera movement, no "
    "animation yet. Then there is an abrupt hard CUT (not a smooth "
    "transition or morph) to the next shot: the exact same pair of shoes, "
    "in the exact same colors and pattern, now resting together side by "
    "side on top of a round matte white rotating display podium in an "
    "empty, plain studio background -- no person, no foot, no leg, no "
    "skin, not even blurred in the background. Both shoes of the pair "
    "must stay together and fully visible at all times after the cut -- "
    "never show only one shoe alone. The podium rotates slowly and gently "
    "in one single consistent direction only (never reversing), while "
    "the camera itself stays completely fixed and static, no camera "
    "movement at all in this second shot. Soft studio lighting, shallow "
    "depth of field, elegant premium footwear e-commerce advertisement "
    "style, vertical mobile-first framing, no added text, no added logos."
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
