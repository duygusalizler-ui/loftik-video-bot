"""
Kurgu: klipleri 1080x1920'ye getirir, birlestirir, Turkce ekran yazilarini
(kanca, urun satiri, kapanis karti) PNG katman olarak bindirir.

ffmpeg sistemde olmasa bile imageio-ffmpeg paketinin getirdigi ffmpeg
kullanilir; drawtext filtresine ihtiyac yok (yazilar Pillow ile ciziliyor).
"""
from __future__ import annotations

import glob
import json
import os
import random
import subprocess

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30

MUSIC_DIR = "assets/music"
MUSIC_VOLUME = float(os.environ.get("MUSIC_VOLUME", "0.18"))  # arka plan muzigi (kisik)
VIDEO_VOLUME = 1.0  # videonun kendi sesi (ayak sesi, sokak) -- KISILMIYOR


def pick_music() -> str | None:
    tracks = sorted(glob.glob(os.path.join(MUSIC_DIR, "*.mp3")) + glob.glob(os.path.join(MUSIC_DIR, "*.m4a")))
    return random.choice(tracks) if tracks else None


def ffmpeg_exe() -> str:
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:  # noqa: BLE001
        return "ffmpeg"


def _run(args: list[str]) -> None:
    proc = subprocess.run([ffmpeg_exe(), "-loglevel", "error", "-y", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg hatası: {proc.stderr[-800:]}")


def duration(path: str) -> float:
    proc = subprocess.run([ffmpeg_exe(), "-i", path], capture_output=True, text=True)
    for line in proc.stderr.splitlines():
        line = line.strip()
        if line.startswith("Duration:"):
            h, m, s = line.split(",")[0].split("Duration:")[1].strip().split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    raise RuntimeError(f"Süre okunamadı: {path}")


def has_audio(path: str) -> bool:
    proc = subprocess.run([ffmpeg_exe(), "-i", path], capture_output=True, text=True)
    return "Audio:" in proc.stderr


def extract_frames(video_path: str, out_dir: str, count: int = 4) -> list[str]:
    """Klipten esit aralikli kareler (kalite kontrolu icin)."""
    os.makedirs(out_dir, exist_ok=True)
    total = duration(video_path)
    paths = []
    for i in range(count):
        t = total * (i + 0.5) / count
        p = os.path.join(out_dir, f"frame_{i}.jpg")
        _run(["-ss", f"{t:.2f}", "-i", video_path, "-frames:v", "1", "-vf", "scale=720:-2", p])
        paths.append(p)
    return paths


def normalize_clip(src: str, dst: str) -> str:
    """1080x1920, 30fps, stereo ses (ses yoksa sessiz ses ekler)."""
    vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,fps={FPS}"
    if has_audio(src):
        _run(["-i", src, "-vf", vf, "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
              "-c:a", "aac", "-ar", "44100", "-ac", "2", dst])
    else:
        _run(["-i", src, "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
              "-vf", vf, "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
              "-c:a", "aac", dst])
    return dst


# ---------------------------------------------------------------------------
# Yazi katmanlari
# ---------------------------------------------------------------------------
def _font(size: int) -> ImageFont.FreeTypeFont:
    for candidate in (
        "DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ):
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap(draw, text: str, font, max_w: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if draw.textlength(test, font=font) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def text_card(path: str, blocks: list[tuple[str, int]], center_y: int) -> str:
    """blocks: [(metin, font_boyu), ...] -- yari saydam kutu icinde ortali."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rendered = []
    for text, size in blocks:
        if not text:
            continue
        f = _font(size)
        for line in _wrap(d, text, f, W - 180):
            b = d.textbbox((0, 0), line, font=f)
            rendered.append((line, f, b))
    if not rendered:
        im.save(path)
        return path
    gap = 20
    total_h = sum(b[3] - b[1] for _, _, b in rendered) + gap * (len(rendered) - 1)
    max_w = max(b[2] - b[0] for _, _, b in rendered)
    top = center_y - total_h // 2
    d.rounded_rectangle(
        ((W - max_w) // 2 - 44, top - 34, (W + max_w) // 2 + 44, top + total_h + 40),
        radius=30, fill=(12, 12, 16, 175),
    )
    y = top
    for line, f, b in rendered:
        w = b[2] - b[0]
        d.text(((W - w) // 2 - b[0], y - b[1]), line, font=f, fill=(255, 255, 255, 255))
        y += b[3] - b[1] + gap
    im.save(path)
    return path


def compose_ad(clips: list[str], brief: dict, product_title: str, price_text: str | None,
               site: str, work_dir: str, output_path: str, music_path: str | None = None) -> str:
    """Klipleri birlestirir + kanca / urun satiri / kapanis kartini bindirir."""
    os.makedirs(work_dir, exist_ok=True)
    norm = [normalize_clip(c, os.path.join(work_dir, f"norm_{i}.mp4")) for i, c in enumerate(clips)]
    durs = [duration(p) for p in norm]
    total = sum(durs)

    hook = text_card(os.path.join(work_dir, "hook.png"), [(brief.get("kanca_metni", ""), 76)], 360)
    product_line = brief.get("urun_satiri") or product_title
    mid = text_card(
        os.path.join(work_dir, "mid.png"),
        [(product_line, 60), (price_text or "", 48)],
        1480,
    )
    end = text_card(
        os.path.join(work_dir, "end.png"),
        [("LOFTIK", 112), (price_text or "", 56), (site.replace("https://", "").replace("www.", ""), 50),
         (f"{brief.get('cta') or 'Şimdi incele'} →", 46)],
        900,
    )

    hook_end = min(3.2, durs[0] - 0.3)
    mid_start = hook_end + 0.6
    end_start = max(mid_start + 2.0, total - 2.8)

    inputs = []
    for p in norm:
        inputs += ["-i", p]
    n = len(norm)
    inputs += ["-i", hook, "-i", mid, "-i", end]
    if music_path:
        inputs += ["-stream_loop", "-1", "-i", music_path]
    concat_in = "".join(f"[{i}:v][{i}:a]" for i in range(n))
    if music_path:
        m = n + 3
        audio = (
            f"{concat_in}concat=n={n}:v=1:a=1[v][va];"
            f"[va]volume={VIDEO_VOLUME}[va2];"
            f"[{m}:a]volume={MUSIC_VOLUME},atrim=0:{total:.2f},"
            f"afade=t=in:d=0.8,afade=t=out:st={max(total - 1.5, 0):.2f}:d=1.5[mu];"
            f"[va2][mu]amix=inputs=2:duration=first:normalize=0[a];"
        )
    else:
        audio = f"{concat_in}concat=n={n}:v=1:a=1[v][a];"
    fc = (
        audio +
        f"[v][{n}:v]overlay=0:0:enable='between(t,0.2,{hook_end:.2f})'[v1];"
        f"[v1][{n + 1}:v]overlay=0:0:enable='between(t,{mid_start:.2f},{end_start - 0.2:.2f})'[v2];"
        f"[v2][{n + 2}:v]overlay=0:0:enable='gte(t,{end_start:.2f})'[vout]"
    )
    _run([*inputs, "-filter_complex", fc, "-map", "[vout]", "-map", "[a]",
          "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", output_path])
    with open(os.path.join(work_dir, "kurgu.json"), "w", encoding="utf-8") as f:
        json.dump({"klipler": durs, "toplam": total}, f)
    return output_path
