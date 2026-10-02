"""Gemini (metin + gorsel) ve Veo (ses efektli video) cagrilari, model yedekli."""
from __future__ import annotations

import json
import re
import time
from pathlib import Path

from PIL import Image, ImageOps

from . import settings


class QuotaError(RuntimeError):
    pass


_client = None


def client():
    global _client
    if _client is None:
        from google import genai

        if not settings.GEMINI_API_KEY:
            raise SystemExit("GEMINI_API_KEY tanımlı değil.")
        _client = genai.Client(api_key=settings.GEMINI_API_KEY)
    return _client


def _mime(p: str) -> str:
    return "image/png" if p.lower().endswith(".png") else "image/jpeg"


def _part(p: str):
    from google.genai import types

    return types.Part.from_bytes(data=Path(p).read_bytes(), mime_type=_mime(p))


def _quota(exc: Exception) -> bool:
    s = str(exc)
    return "429" in s or "RESOURCE_EXHAUSTED" in s


def text_json(prompt: str, images: list[str] | None = None) -> dict:
    from google.genai import types

    contents = [prompt] + [_part(p) for p in (images or [])]
    cfg = types.GenerateContentConfig(response_mime_type="application/json", temperature=1.0)
    last = None
    for model in settings.TEXT_MODELS:
        try:
            resp = client().models.generate_content(model=model, contents=contents, config=cfg)
            t = re.sub(r"^```(?:json)?|```$", "", (resp.text or "").strip(), flags=re.M).strip()
            return json.loads(t[t.find("{"): t.rfind("}") + 1])
        except Exception as exc:  # noqa: BLE001
            if "404" in str(exc) or "NOT_FOUND" in str(exc):
                last = exc
                continue
            if _quota(exc):
                raise QuotaError(str(exc)) from exc
            raise
    raise last or RuntimeError("Kullanılabilir Gemini metin modeli yok.")


def _vertical(path: str) -> str:
    img = ImageOps.fit(Image.open(path).convert("RGB"), (1080, 1920), method=Image.LANCZOS, centering=(0.5, 0.55))
    out = str(Path(path).with_suffix(".jpg"))
    img.save(out, quality=93)
    return out


def image(prompt: str, refs: list[str], out_png: str) -> str:
    from google.genai import types

    parts = [_part(p) for p in refs] + [prompt]
    try:
        cfg = types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"],
                                          image_config=types.ImageConfig(aspect_ratio="9:16"))
    except Exception:  # noqa: BLE001
        cfg = types.GenerateContentConfig(response_modalities=["TEXT", "IMAGE"])
    last = None
    for model in settings.IMAGE_MODELS:
        try:
            resp = client().models.generate_content(model=model, contents=parts, config=cfg)
        except Exception as exc:  # noqa: BLE001
            if "404" in str(exc) or "NOT_FOUND" in str(exc):
                last = exc
                continue
            if _quota(exc):
                raise QuotaError(str(exc)) from exc
            raise
        for part in resp.candidates[0].content.parts:
            data = getattr(getattr(part, "inline_data", None), "data", None)
            if data:
                print(f"    (görsel modeli: {model})")
                Path(out_png).write_bytes(data)
                return _vertical(out_png)
        last = RuntimeError(f"{model} görsel döndürmedi")
    raise last or RuntimeError("Görsel üretilemedi.")


def _kling_fal(start_image: str, prompt: str, out_mp4: str, negative: str = "") -> str:
    """fal.ai uzerinden Kling 3.0 Pro: baslangic karesinden ses efektli, cok cekimli klip."""
    import base64

    import requests

    data_uri = f"data:{_mime(start_image)};base64," + base64.b64encode(Path(start_image).read_bytes()).decode()
    body = {"start_image_url": data_uri, "prompt": prompt[:2500], "duration": str(settings.CLIP_SECONDS),
            "generate_audio": True, "negative_prompt": negative or "blur, distort, and low quality"}
    last = None
    for scheme in ("Key", "Api-Key"):  # fal'in iki yetki basligi bicimi
        headers = {"Authorization": f"{scheme} {settings.FAL_KEY}", "Content-Type": "application/json"}
        r = requests.post(f"https://queue.fal.run/{settings.KLING_MODEL}", json=body, headers=headers, timeout=120)
        if r.status_code in (401, 403):
            last = r
            continue
        if r.status_code == 429 or "balance" in r.text.lower() or "exhausted" in r.text.lower():
            raise QuotaError(f"fal.ai: {r.status_code} {r.text[:300]}")
        r.raise_for_status()
        sub = r.json()
        status_url = sub.get("status_url") or f"https://queue.fal.run/{settings.KLING_MODEL}/requests/{sub['request_id']}/status"
        result_url = sub.get("response_url") or f"https://queue.fal.run/{settings.KLING_MODEL}/requests/{sub['request_id']}"
        waited = 0
        while True:
            s = requests.get(status_url, headers=headers, timeout=60).json()
            if s.get("status") == "COMPLETED":
                break
            if s.get("status") in ("FAILED", "ERROR") or s.get("error"):
                raise RuntimeError(f"Kling üretemedi: {s}")
            time.sleep(10)
            waited += 10
            if waited > 900:
                raise RuntimeError("Kling klibi 15 dakikada bitmedi.")
        res = requests.get(result_url, headers=headers, timeout=60).json()
        url = (res.get("video") or {}).get("url")
        if not url:
            raise RuntimeError(f"Kling sonucu video içermiyor: {str(res)[:300]}")
        Path(out_mp4).write_bytes(requests.get(url, timeout=300).content)
        return out_mp4
    raise RuntimeError(f"fal.ai yetki hatası (FAL_KEY doğru mu?): {last.status_code} {last.text[:200]}")


def video(start_image: str, prompt: str, out_mp4: str, negative: str = "") -> str:
    """Baslangic karesinden ses EFEKTLI klip (konusma/muzik yok). Motor: settings.VIDEO_PROVIDER."""
    if settings.VIDEO_PROVIDER == "kling":
        if not settings.FAL_KEY:
            raise SystemExit("Kling seçili ama FAL_KEY tanımlı değil.")
        return _kling_fal(start_image, prompt, out_mp4, negative)
    from google.genai import types

    img = types.Image(image_bytes=Path(start_image).read_bytes(), mime_type=_mime(start_image))
    base = dict(aspect_ratio="9:16", number_of_videos=1, duration_seconds=settings.CLIP_SECONDS,
                negative_prompt=negative or None)
    op = None
    for extra in ({"generate_audio": True}, {}):  # Gemini API generate_audio'yu reddederse onsuz dene
        try:
            op = client().models.generate_videos(model=settings.VIDEO_MODEL, prompt=prompt, image=img,
                                                 config=types.GenerateVideosConfig(**base, **extra))
            break
        except Exception as exc:  # noqa: BLE001
            if _quota(exc):
                raise QuotaError(str(exc)) from exc
            if extra and ("generate_audio" in str(exc) or "INVALID_ARGUMENT" in str(exc)):
                continue
            raise
    waited = 0
    while not op.done:
        time.sleep(15)
        waited += 15
        if waited > 720:
            raise RuntimeError("Veo klibi 12 dakikada bitmedi.")
        op = client().operations.get(op)
    if not op.response or not op.response.generated_videos:
        raise RuntimeError(f"Veo klip üretemedi: {getattr(op, 'error', op)}")
    v = op.response.generated_videos[0]
    client().files.download(file=v.video)
    v.video.save(out_mp4)
    return out_mp4
