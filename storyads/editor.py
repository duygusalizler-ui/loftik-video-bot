"""
Kurgu: sahne klipleri -> yumusak gecisli (xfade) tek video.

- Seslendirme YOK: klibin kendi ses efektleri (Kling/Veo urettigi) korunur,
  altina kisik muzik eklenir.
- Ekran yazilari "organik" gorunur: reklam kutusu degil, Reels/TikTok'taki
  gibi beyaz kutulu kanca + konturlu altyazi.
- Sonda urun fotografi / fiyat karti YOK; video hikayenin vurucu cumlesiyle biter.
"""
from __future__ import annotations

import os
import re
import subprocess

from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
XFADE = 0.45  # gecis suresi (sn)
FONT_PATHS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "DejaVuSans-Bold.ttf",
)
_EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿️]")


def ffmpeg() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        return "ffmpeg"


def run(args: list[str]) -> None:
    p = subprocess.run([ffmpeg(), "-loglevel", "error", "-y", *args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"ffmpeg hatası: {p.stderr[-800:]}")


def duration(path: str) -> float:
    err = subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True).stderr
    for line in err.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            h, m, s = line.split(",")[0].split()[1].split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"Süre okunamadı: {path}")


def has_audio(path: str) -> bool:
    return "Audio:" in subprocess.run([ffmpeg(), "-i", path], capture_output=True, text=True).stderr


def _font(size: int):
    for p in FONT_PATHS:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(d, text, font, max_w):
    lines, cur = [], ""
    for w in text.split():
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=font) <= max_w or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + ([cur] if cur else [])


def text_png(path: str, text: str, style: str, y: int | None = None) -> str:
    """style: kanca (beyaz kutu, siyah yazi, ust) | altyazi (konturlu, alt) | final (buyuk, orta)."""
    text = _EMOJI.sub("", text or "").strip()
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not text:
        im.save(path)
        return path
    d = ImageDraw.Draw(im)
    # final ustte: karakterlerin yuzu genelde ekranin ortasinda kaliyor
    size, cy = {"kanca": (66, 360), "altyazi": (60, 1450), "final": (88, 330)}[style]
    cy = y or cy
    f = _font(size)
    lines = _wrap(d, text, f, W - 200)
    boxes = [d.textbbox((0, 0), ln, font=f, stroke_width=6) for ln in lines]
    gap = 14
    th = sum(b[3] - b[1] for b in boxes) + gap * (len(lines) - 1)
    y = cy - th // 2
    if style == "kanca":
        mw = max(b[2] - b[0] for b in boxes)
        d.rounded_rectangle(((W - mw) // 2 - 36, y - 28, (W + mw) // 2 + 36, y + th + 30), radius=26, fill=(255, 255, 255, 240))
    for ln, b in zip(lines, boxes):
        x = (W - (b[2] - b[0])) // 2 - b[0]
        if style == "kanca":
            d.text((x, y - b[1]), ln, font=f, fill=(15, 15, 15, 255))
        else:
            d.text((x, y - b[1]), ln, font=f, fill=(255, 255, 255, 255), stroke_width=7, stroke_fill=(0, 0, 0, 255))
        y += b[3] - b[1] + gap
    im.save(path)
    return path


def _scene_part(work: str, i: int, clip: str, text: str | None, hook: str | None,
                final: str | None, speed: float, start: float, end: float | None,
                final_y: int | None = None, final_at: float | None = None,
                hook_y: int | None = None) -> tuple[str, float]:
    """Klibi dikey 1080x1920'ye getirir, yazilari bindirir. Ses (efektler) korunur.
    start/end: klibin kullanilacak araligi (hatali anlari kesmek icin)."""
    end = min(end or 1e9, duration(clip))
    L = (end - start) / speed
    ins = ["-ss", f"{start}", "-i", clip]
    if not has_audio(clip):
        ins += ["-f", "lavfi", "-t", f"{L + 1:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]
        a_src = "[1:a]"
        k = 2
    else:
        a_src = "[0:a]"
        k = 1
    fc = (f"[0:v]setpts=PTS/{speed},scale={W}:{H}:force_original_aspect_ratio=increase,"
          f"crop={W}:{H},fps={FPS},setsar=1[v0]")
    last = "[v0]"
    layers = []
    if hook:
        layers.append((text_png(os.path.join(work, f"kanca_{i}.png"), hook, "kanca", hook_y), 0.1, L - XFADE))
    if text:
        layers.append((text_png(os.path.join(work, f"yazi_{i}.png"), text, "altyazi"), XFADE + 0.1, L - XFADE))
    if final:
        t0 = final_at if final_at is not None else max(min(L * 0.35, 1.6), XFADE + 0.3)
        layers.append((text_png(os.path.join(work, f"final_{i}.png"), final, "final", final_y), t0, L + 1))
    for n, (png, t0, t1) in enumerate(layers):
        ins += ["-i", png]
        fc += f";{last}[{k}:v]overlay=0:0:enable='between(t,{t0:.2f},{t1:.2f})'[l{n}]"
        last = f"[l{n}]"
        k += 1
    tempo = f",atempo={speed}" if abs(speed - 1) > 0.01 else ""
    fc += f";{a_src}aformat=sample_rates=44100:channel_layouts=stereo{tempo}[a]"
    out = os.path.join(work, f"parca_{i}.mp4")
    run([*ins, "-filter_complex", fc, "-map", last, "-map", "[a]", "-t", f"{L:.3f}",
         "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", out])
    return out, duration(out)


def compose(scenes: list[dict], output: str, work: str, music: str | None = None,
            music_volume: float = 0.22, sfx_volume: float = 1.0, speed: float = 1.0,
            trim_start: float = 0.15, transitions: list[str] | None = None) -> float:
    """
    scenes: [{"clip": path, "text": altyazi, "hook": kanca (ilk sahne), "final": son cumle (son sahne),
              "bas": sn, "son": sn, "final_y": piksel, "final_bas": sn}]
    bas/son: klibin kullanilacak araligi; final_y/final_bas: final yazisinin yuksekligi ve
    sahnede ne zaman cikacagi (karakterin yuzunu kapatmasin diye). Hepsi opsiyonel.
    Doner: video suresi (sn).
    """
    os.makedirs(work, exist_ok=True)
    parts = [_scene_part(work, i, s["clip"], s.get("text"), s.get("hook"), s.get("final"), speed,
                         s.get("bas", trim_start), s.get("son"), s.get("final_y"), s.get("final_bas"),
                         s.get("hook_y"))
             for i, s in enumerate(scenes)]
    trans = (transitions or [])[: len(parts) - 1]
    trans += ["fade"] * (len(parts) - 1 - len(trans))
    ins, fc, acc = [], "", 0.0
    for p, _ in parts:
        ins += ["-i", p]
    v_last, a_last = "[0:v]", "[0:a]"
    for k in range(1, len(parts)):
        acc += parts[k - 1][1] - XFADE
        fc += (f"{v_last}[{k}:v]xfade=transition={trans[k - 1]}:duration={XFADE}:offset={acc:.3f}[v{k}];"
               f"{a_last}[{k}:a]acrossfade=d={XFADE}[a{k}];")
        v_last, a_last = f"[v{k}]", f"[a{k}]"
    total = acc + parts[-1][1]
    fc += f"{a_last}volume={sfx_volume}[sfx];"
    if music:
        m = len(parts)
        ins += ["-stream_loop", "-1", "-i", music]
        fc += (f"[{m}:a]aformat=sample_rates=44100:channel_layouts=stereo,atrim=0:{total:.2f},"
               f"volume={music_volume},afade=t=in:d=0.6,afade=t=out:st={max(total - 1.8, 0):.2f}:d=1.8[mu];"
               f"[sfx][mu]amix=inputs=2:duration=first:normalize=0,")
    else:
        fc += "[sfx]"
    fc += f"loudnorm=I=-14:TP=-1.5,atrim=0:{total:.2f}[aout]"
    run([*ins, "-filter_complex", fc, "-map", v_last, "-map", "[aout]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart", output])
    return total


def contact_sheet(video: str, out: str, n: int = 6) -> str:
    """Kontrol icin videodan n kare."""
    T = duration(video)
    tmp = []
    for i in range(n):
        p = f"{out}.{i}.jpg"
        run(["-ss", f"{T * (i + 0.5) / n:.2f}", "-i", video, "-frames:v", "1", "-vf", "scale=240:-2", p])
        tmp.append(Image.open(p))
    w, h = tmp[0].size
    sheet = Image.new("RGB", (w * n, h))
    for i, im in enumerate(tmp):
        sheet.paste(im, (i * w, 0))
    sheet.save(out, quality=85)
    for i in range(n):
        os.remove(f"{out}.{i}.jpg")
    return out
