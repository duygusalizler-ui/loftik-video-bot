"""Uctan uca: urun linki -> hikaye plani -> sahne gorselleri -> ses efektli klipler -> kurgu."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

from . import editor, genai, music, planner, product as product_mod, qa, settings
from .brand import Brand

STYLE = ("Hybrid live-action + animation shot, like a modern family movie: the animal characters are "
         "cute stylized 3D-animated characters standing and dressed like people; the ENTIRE background is "
         "a REAL photograph of a real everyday location in Turkey with natural light and real people. ")
PRODUCT_RULE = (" The product must be the EXACT real product from the reference photos (same shape, colors, "
                "materials, sole, details) and must look 100% PHOTOREALISTIC like real product photography, "
                "NOT cartoon, NOT stylized. Correct anatomy, exactly two feet if feet are visible, no extra "
                "products floating around.")
NO_TEXT = " No text, no letters, no logos, no brand names anywhere. Vertical 9:16."
MOTION_RULE = (" Normal real-time speed, NO slow motion, one continuous shot, slight handheld camera. "
               "Keep characters, background and product identical to the first frame. Product stays a real "
               "photorealistic product in every frame.")
NEGATIVE = "speech, talking, dialogue, narration, voice, singing, music, slow motion, text, subtitles, logo, watermark"


@dataclass
class Result:
    video: str | None
    plan: dict
    caption: str = ""
    pinned_comment: str = ""
    qa_log: list = field(default_factory=list)


def _scene_image(i: int, scene: dict, plan: dict, prod, prev_img: str | None, work: str, log: list) -> str | None:
    prompt = STYLE + f"Main character: {plan.get('karakter_tarifi', '')}. "
    if plan.get("yan_karakterler"):
        prompt += "Other characters: " + "; ".join(plan["yan_karakterler"]) + ". "
    if prev_img:
        prompt += "Keep the characters EXACTLY as in the last reference image (same design, clothes). "
    prompt += scene["gorsel_prompt"]
    if scene.get("urun_gorunur", True):
        prompt += PRODUCT_RULE
    prompt += NO_TEXT
    refs = prod.gorseller[:2] + ([prev_img] if prev_img else [])
    best = (None, -1)
    for t in range(1, settings.IMAGE_TRIES + 1):
        try:
            img = genai.image(prompt, refs, os.path.join(work, f"sahne{i}_{t}.png"))
        except genai.QuotaError:
            raise
        except Exception as exc:  # noqa: BLE001
            print(f"  sahne {i + 1} görsel hatası: {exc}")
            continue
        r = qa.score(prod.gorseller, [img], scene.get("urun_gorunur", True), prev_img)
        log.append({"asama": f"sahne{i + 1}_gorsel", "deneme": t, **r})
        print(f"  sahne {i + 1} görsel {t}: {r['puan']}/10 {r.get('hatalar') or ''}")
        if r["puan"] > best[1]:
            best = (img, r["puan"])
        if r["gecti"]:
            return img
    return best[0] if best[1] >= settings.QA_MIN else None


def _scene_clip(i: int, scene: dict, img: str, prod, work: str, log: list) -> tuple | None:
    prompt = scene["hareket_prompt"] + MOTION_RULE + f" SOUND: {scene.get('ses_efekti', 'natural ambience')}. " \
             "Sound effects and ambience only: no speech, no voices, no music."
    for t in range(1, settings.CLIP_TRIES + 1):
        out = os.path.join(work, f"klip{i}_{t}.mp4")
        try:
            genai.video(img, prompt, out, NEGATIVE)
        except genai.QuotaError:
            raise
        except Exception as exc:  # noqa: BLE001
            print(f"  sahne {i + 1} klip hatası: {exc}")
            continue
        # kare kare kontrol: ~0.6 sn arayla kareler, hatali anlar kesilir
        T = editor.duration(out)
        n = max(6, int(T / 0.6))
        times = [round(T * (k + 0.5) / n, 2) for k in range(n)]
        frames = []
        for k, ts in enumerate(times):
            fp = os.path.join(work, f"kare{i}_{t}_{k}.jpg")
            editor.run(["-ss", f"{ts:.2f}", "-i", out, "-frames:v", "1", "-vf", "scale=540:-2", fp])
            frames.append(fp)
        r = qa.score_clip(prod.gorseller, frames, times, T, start_image=img)
        log.append({"asama": f"sahne{i + 1}_klip", "deneme": t, **r})
        print(f"  sahne {i + 1} klip {t}: {r['puan']}/10 temiz aralık={r.get('aralik')} {r.get('hatali_kareler') or ''}")
        if r["gecti"]:
            return out, r["aralik"], r.get("son_yuz_konumu")
    return None


def run(brand: Brand, product_url: str, out_dir: str, fmt: str | None = None,
        karakter: str | None = None, extra_images: list | None = None) -> Result:
    work = os.path.join(out_dir, "is")
    os.makedirs(work, exist_ok=True)
    print(f"[1/5] Ürün okunuyor: {product_url}")
    prod = product_mod.fetch(product_url, os.path.join(work, "urun"), extra_images=extra_images)
    print(f"      {prod.ad} | {prod.fiyat} | {len(prod.gorseller)} fotoğraf")

    fmt, karakter = planner.choose(brand, fmt, karakter)
    print(f"[2/5] Hikâye yazılıyor: format={fmt}, karakter={karakter}")
    plan = planner.make_plan(brand, prod, fmt, karakter)
    with open(os.path.join(out_dir, "plan.json"), "w", encoding="utf-8") as f:
        json.dump(plan, f, ensure_ascii=False, indent=1)

    print("[3/5] Sahneler üretiliyor")
    log: list = []
    scenes, prev = [], None
    for i, sc in enumerate(plan["sahneler"]):
        img = _scene_image(i, sc, plan, prod, prev, work, log)
        if not img:
            print(f"  sahne {i + 1} atlandı (kalite kontrolünden geçen görsel yok)")
            continue
        prev = prev or img  # karakter referansi: ilk gecen sahne
        got = _scene_clip(i, sc, img, prod, work, log)
        if got:
            clip, (bas, son), yuz = got
            scenes.append({"clip": clip, "bas": bas, "son": son, "text": sc.get("ekran_yazisi") or None,
                           "rol": sc.get("rol"), "yuz": yuz})
    if len(scenes) < 3:
        print("Yeterli sahne yok, video üretilmedi.")
        return Result(None, plan, qa_log=log)

    print("[4/5] Kurgu")
    scenes[0]["hook"], scenes[0]["text"] = plan.get("kanca"), None
    scenes[-1]["final"], scenes[-1]["text"] = plan.get("final_yazi"), None
    # final yazisi karakterin yuzunu kapatmasin: yuz ustteyse yazi ortaya iner
    if scenes[-1].get("yuz") == "ust":
        scenes[-1]["final_y"] = 900
    track, credit = music.pick(plan.get("muzik_modu") or brand.muzik_modu)
    video = os.path.join(out_dir, "video.mp4")
    total = editor.compose(scenes, video, os.path.join(work, "kurgu"), music=track, music_volume=settings.MUSIC_VOLUME)
    if total < 15:
        log.append({"asama": "sure", "deneme": 1, "gecti": False, "puan": 0,
                    "hatalar": [f"video {total:.1f} sn (hedef 15-30); hatalı anlar kesildiği için kısaldı"]})
    editor.contact_sheet(video, os.path.join(out_dir, "kareler.jpg"))

    print("[5/5] Açıklama")
    caption = planner.caption_text(brand, plan, credit)
    pinned = plan.get("sabit_yorum", "")
    for name, txt in (("aciklama.txt", caption), ("sabit_yorum.txt", pinned)):
        with open(os.path.join(out_dir, name), "w", encoding="utf-8") as f:
            f.write(txt)
    with open(os.path.join(out_dir, "kalite.json"), "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=1)
    planner.remember(brand, fmt, karakter)
    return Result(video, plan, caption, pinned, log)
