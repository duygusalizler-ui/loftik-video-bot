"""
"reklam" modu -- bir urun icin bastan sona reklam videosu uretir.

  1. Rakip reklam analizi -> brief (competitor_ads.build_brief)
  2. Her sahne icin: gercek urun fotografindan sahne gorseli (Gemini image)
     -> kalite kontrolu (quality_check) -> gecemezse yeniden (en fazla N)
  3. Her sahne gorselinden ~8 sn video klibi (Veo)
     -> klipten 4 kare cikar -> kalite kontrolu -> gecemezse yeniden
  4. Gecen klipler birlestirilir, Turkce yazilar + kapanis karti eklenir
  5. Sonuc + rakip analizi ozeti + kalite puanlari dondurulur

Hic klip kalite kontrolunden gecemezse video GONDERILMEZ (hatali icerik
sana gelmesin diye); main.py bu durumda gercek fotograflarla kaydirmali
gonderi yollar.
"""
from __future__ import annotations

import os
import time
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageOps

from . import competitor_ads, config, quality_check, video_edit
from .gemini_video import QuotaExceededError


@dataclass
class AdResult:
    video_path: str | None
    brief: dict
    qa_log: list = field(default_factory=list)
    scene_images: list = field(default_factory=list)


def _client():
    from google import genai

    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY tanımlı değil (GitHub Secrets'a eklemeyi unutma).")
    return genai.Client(api_key=config.GEMINI_API_KEY)


def _mime(path: str) -> str:
    return "image/png" if path.lower().endswith(".png") else "image/jpeg"


def _to_vertical(path: str) -> str:
    img = Image.open(path).convert("RGB")
    img = ImageOps.fit(img, (1080, 1920), method=Image.LANCZOS, centering=(0.5, 0.6))
    out = str(Path(path).with_suffix(".9x16.jpg"))
    img.save(out, quality=92)
    return out


SCENE_IMAGE_RULES = (
    " The product MUST be EXACTLY the shoe in the reference image: same shape, same upper "
    "color, same sole color and thickness, same details. Do not add logos or text anywhere. "
    "Exactly two feet, anatomically correct. Vertical 9:16 composition, shoes large and in "
    "sharp focus. MUST NOT look AI-generated: shot on a normal smartphone by a real person, "
    "everyday real location (Turkish city street, cafe, office, home entrance), natural "
    "imperfect light, slight real-world clutter, real fabric wrinkles, real dust/texture on "
    "the ground, no cinematic grading, no HDR glow, no bokeh fireworks, no perfect symmetry, "
    "no plastic skin, no overly glossy surfaces, no fantasy or surreal elements."
)


def generate_scene_image(reference_path, prompt: str, out_path: str, product_title: str = "") -> str:
    """reference_path: tek yol ya da yol listesi (ilki ana foto, digerleri farkli acilar)."""
    from google.genai import types

    client = _client()
    refs = [reference_path] if isinstance(reference_path, str) else list(reference_path)
    parts = [types.Part.from_bytes(data=Path(r).read_bytes(), mime_type=_mime(r)) for r in refs]
    product_line = (
        f"The product is: {product_title}. The {len(refs)} reference photo(s) show this SAME exact "
        "product from different angles -- copy its construction exactly (e.g. a chelsea boot has "
        "NO laces and has elastic side panels; keep leather vs suede texture exactly as shown; keep "
        "the same shaft height). "
        if product_title else ""
    )
    parts.append(product_line + prompt + SCENE_IMAGE_RULES)
    cfg_kwargs = {"response_modalities": ["TEXT", "IMAGE"]}
    try:
        cfg = types.GenerateContentConfig(**cfg_kwargs, image_config=types.ImageConfig(aspect_ratio="9:16"))
    except Exception:  # noqa: BLE001 -- eski SDK'da image_config yoksa
        cfg = types.GenerateContentConfig(**cfg_kwargs)
    resp = None
    for model in dict.fromkeys([config.GEMINI_IMAGE_MODEL, "gemini-3-pro-image", "gemini-2.5-flash-image"]):
        try:
            resp = client.models.generate_content(model=model, contents=parts, config=cfg)
            break
        except Exception as exc:  # noqa: BLE001
            if "404" in str(exc) or "NOT_FOUND" in str(exc):
                print(f"UYARI: görsel modeli '{model}' kullanılamıyor, sıradaki deneniyor.")
                continue
            raise
    if resp is None:
        raise RuntimeError("Kullanılabilir Gemini görsel modeli bulunamadı.")
    for part in resp.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline is not None and getattr(inline, "data", None):
            Path(out_path).write_bytes(inline.data)
            return _to_vertical(out_path)
    raise RuntimeError("Gemini sahne görseli döndürmedi.")


VIDEO_RULES = (
    " Keep the shoes EXACTLY identical to the first frame in every frame: same shape, same "
    "colors, same sole color. No new logos or text. Exactly two feet and two legs, no extra "
    "limbs. One continuous shot, no cuts, no transitions. REAL-TIME SPEED: normal everyday "
    "walking pace at 1x speed, brisk natural steps, ABSOLUTELY NO slow motion, no floaty or "
    "dreamy movement, no lingering camera; energetic like a quick phone clip. No water splashes. Looks like real handheld smartphone footage, not CGI, not "
    "cinematic. Natural ambient sound only (footsteps, street, room tone): NO speech, NO "
    "voices, NO singing, NO music."
)


def generate_clip(image_path: str, motion_prompt: str, out_path: str) -> str:
    from google.genai import types

    client = _client()
    image_arg = types.Image(image_bytes=Path(image_path).read_bytes(), mime_type=_mime(image_path))
    try:
        cfg = types.GenerateVideosConfig(aspect_ratio="9:16", number_of_videos=1, duration_seconds=8)
    except Exception:  # noqa: BLE001
        cfg = types.GenerateVideosConfig(aspect_ratio="9:16", number_of_videos=1)
    try:
        op = client.models.generate_videos(
            model=config.VIDEO_MODEL, prompt=motion_prompt + VIDEO_RULES, image=image_arg, config=cfg
        )
    except Exception as exc:  # noqa: BLE001
        if "429" in str(exc) or "RESOURCE_EXHAUSTED" in str(exc):
            raise QuotaExceededError(f"Veo kotası doldu: {exc}") from exc
        raise
    waited = 0
    while not op.done:
        time.sleep(15)
        waited += 15
        if waited > 600:
            raise RuntimeError("Veo klibi 10 dakikada tamamlanmadı.")
        op = client.operations.get(op)
    if not op.response or not op.response.generated_videos:
        raise RuntimeError(f"Veo klip üretemedi: {op}")
    vid = op.response.generated_videos[0]
    client.files.download(file=vid.video)
    vid.video.save(out_path)
    return out_path


def _best_scene_image(reference: str, prompt: str, work: str, idx: int, qa_log: list,
                      refs: list | None = None, product_title: str = "") -> str | None:
    best = (None, -1)
    for attempt in range(1, config.SCENE_IMAGE_ATTEMPTS + 1):
        try:
            print(f"Sahne {idx + 1}: görsel üretiliyor (deneme {attempt})...")
            img = generate_scene_image(
                refs or reference, prompt, os.path.join(work, f"scene{idx}_{attempt}.png"), product_title
            )
        except QuotaExceededError:
            raise
        except Exception as exc:  # noqa: BLE001
            print(f"UYARI: sahne görseli üretilemedi: {exc}")
            continue
        qa = quality_check.safe_score(reference, [img])
        qa_log.append({"asama": f"sahne{idx + 1}_gorsel", "deneme": attempt, **qa})
        print(f"  kalite puanı: {qa['puan']}/10 {qa.get('hatalar') or ''}")
        if qa["puan"] > best[1]:
            best = (img, qa["puan"])
        if qa["gecti"]:
            return img
    return best[0] if best[1] >= config.QA_MIN_SCORE else None


def _good_clip(reference: str, scene_img: str, motion: str, work: str, idx: int, qa_log: list) -> str | None:
    for attempt in range(1, config.CLIP_ATTEMPTS + 1):
        clip = os.path.join(work, f"clip{idx}_{attempt}.mp4")
        try:
            print(f"Sahne {idx + 1}: video klibi üretiliyor (deneme {attempt}, birkaç dakika)...")
            generate_clip(scene_img, motion, clip)
        except QuotaExceededError:
            raise
        except Exception as exc:  # noqa: BLE001
            print(f"UYARI: klip üretilemedi: {exc}")
            continue
        frames = video_edit.extract_frames(clip, os.path.join(work, f"frames{idx}_{attempt}"))
        qa = quality_check.safe_score(reference, frames)
        qa_log.append({"asama": f"sahne{idx + 1}_klip", "deneme": attempt, **qa})
        print(f"  klip kalite puanı: {qa['puan']}/10 {qa.get('hatalar') or ''}")
        if qa["gecti"]:
            return clip
    return None


ALT_MOTION = (
    "Same scene, different shot: the camera starts close on the shoes and quickly pulls back and "
    "rises to reveal the full outfit while the person takes a few brisk steps forward at normal "
    "real-time walking speed; natural handheld phone movement, no slow motion."
)


def build_ad(product, reference_path: str, is_boot: bool, work: str, output_path: str,
             extra_refs: list | None = None) -> AdResult:
    os.makedirs(work, exist_ok=True)
    print("Rakip reklam analizi yapılıyor...")
    brief = competitor_ads.build_brief(product, is_boot=is_boot)
    print(f"Brief hazır: kanca='{brief['kanca_metni']}', {len(brief['sahneler'])} sahne")

    qa_log: list = []
    clips, scene_images = [], []
    refs = [reference_path] + list(extra_refs or [])[:2]
    for idx, scene in enumerate(brief["sahneler"]):
        motion = scene["hareket_prompt"]
        img = _best_scene_image(reference_path, scene["gorsel_prompt"], work, idx, qa_log, refs, product.title)
        if not img and scene_images:
            # Bu sahnenin gorseli tutmadi: kontrolden gecmis onceki sahne gorselini
            # farkli bir kamera hareketiyle tekrar kullan (video kisa kalmasin).
            print(f"Sahne {idx + 1}: görsel tutmadı, önceki sahne görseli farklı kamera hareketiyle kullanılıyor.")
            img, motion = scene_images[-1], ALT_MOTION
        if not img:
            print(f"Sahne {idx + 1}: kalite kontrolünden geçen görsel yok, sahne atlandı.")
            continue
        scene_images.append(img)
        clip = _good_clip(reference_path, img, motion, work, idx, qa_log)
        if clip:
            clips.append(clip)
        else:
            print(f"Sahne {idx + 1}: kalite kontrolünden geçen klip yok, sahne atlandı.")

    if not clips:
        return AdResult(None, brief, qa_log, scene_images)

    video_edit.compose_ad(
        clips, brief, product.title, product.price_text, config.SITE_BASE_URL,
        os.path.join(work, "kurgu"), output_path, music_path=video_edit.pick_music(),
    )
    return AdResult(output_path, brief, qa_log, scene_images)


def qa_summary(result: AdResult) -> str:
    passed = [q for q in result.qa_log if q.get("gecti")]
    failed = [q for q in result.qa_log if not q.get("gecti")]
    lines = [f"✅ Kalite kontrolü: {len(passed)} geçti, {len(failed)} elendi (eşik {config.QA_MIN_SCORE}/10)"]
    for q in failed[:4]:
        err = "; ".join(q.get("hatalar") or [])[:120]
        lines.append(f"• {q['asama']} deneme {q['deneme']}: {q['puan']}/10 {err}")
    return "\n".join(lines)
