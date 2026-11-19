"""Haftalık üretim yardımcıları (önceden scratchpad'deki rec/got/mksrt/thumb betikleri; ortam sıfırlanınca kayboluyordu).

  python -m uh.weekly rec ep009 sub clip 15 1=JOB 2=JOB          # gönderimi deftere yaz
  python -m uh.weekly got ep009 image 1=JOB=URL 2=JOB=URL        # indir + sonucu yaz (image|clip)
  python -m uh.weekly voice ep009 FILE                           # "n tarih_jobid" satırları → audio_eleven_raw + audio_en
  python -m uh.weekly srt ep009 OUT.srt                          # anlatım seslerinden zamanlanmış İngilizce altyazı
  python -m uh.weekly thumbs ep009 "NO|SHOES" "1944"              # thumb_bg.png → teslim/thumb_A/B/C
  python -m uh.weekly chapters ep009                             # YouTube bölüm zamanları
"""
from __future__ import annotations

import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

from . import config as C
from . import state as S
from .assemble import duration

CDN = "https://d8j0ntlcm91z4.cloudfront.net/user_3JNaSHcr3JhGhtM4azgveIkjvu0/hf_"  # + "TARİH_SAAT_jobid"
VOICE_FX = ("highpass=f=70,equalizer=f=250:t=q:w=1.2:g=-2,equalizer=f=3200:t=q:w=1.0:g=3.5,treble=g=2:f=8000,"
            "acompressor=threshold=-20dB:ratio=3:attack=5:release=120:makeup=3,loudnorm=I=-16:TP=-1.5")


def _n(x: str):
    return int(x) if x.isdigit() else x


def rec(ep_id: str, mode: str, kind: str, credits: str, *pairs: str) -> None:
    for a in pairs:
        n, job = a.split("=", 1)
        ep = S.load_episode(ep_id)
        if mode == "sub":
            S.record_submit(ep, _n(n), kind, job.split("=")[0], float(credits))
        else:
            j, url = job.split("=", 1)
            S.record_result(ep, _n(n), kind, j, True, url=url)
    print("harcanan", S.spent(episode=ep_id))


def _curl(url: str, out) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["curl", "-sS", "-f", "-o", str(out), url], check=True)


def got(ep_id: str, kind: str, *triples: str) -> None:
    work = C.BUILD_DIR / ep_id
    jobs = []
    for a in triples:
        n, j, url = a.split("=", 2)
        ep = S.load_episode(ep_id)
        S.record_result(ep, _n(n), kind, j, True, url=url)
        if isinstance(_n(n), int):
            ext, sub = ("png", "images") if kind == "image" else ("mp4", "clips")
            jobs.append((url, work / sub / f"{int(n):03d}.{ext}"))
        else:
            jobs.append((url, work / "refs" / f"{n}.png"))
    with ThreadPoolExecutor(8) as p:
        list(p.map(lambda t: _curl(*t), jobs))
    print("ok", len(jobs))


def voice(ep_id: str, listfile: str) -> None:
    work = C.BUILD_DIR / ep_id
    (work / "audio_eleven_raw").mkdir(parents=True, exist_ok=True)
    (work / "audio_en").mkdir(parents=True, exist_ok=True)
    rows = [l.split() for l in open(listfile) if l.strip()]

    def one(r):
        n, tag = int(r[0]), r[1]
        raw = work / "audio_eleven_raw" / f"{n:03d}.mp3"
        _curl(f"{CDN}{tag}.mp3", raw)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af", VOICE_FX, "-ar", "44100", "-b:a", "192k",
                        str(work / "audio_en" / f"{n:03d}.mp3")], check=True)
        return n, duration(work / "audio_en" / f"{n:03d}.mp3")

    with ThreadPoolExecutor(8) as p:
        res = sorted(p.map(one, rows))
    print(" ".join(f"{n}:{d:.1f}" for n, d in res), "| toplam", round(sum(d for _, d in res) / 60, 2), "dk")


def _silences(p):
    r = subprocess.run(["ffmpeg", "-i", str(p), "-af", "silencedetect=n=-35dB:d=0.18", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", r)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", r)]
    return list(zip(st, en + [None] * (len(st) - len(en))))


def _chunks(txt, mx=84):
    parts = [p.strip() for p in re.split(r"(?<=[.!?…:])\s+", txt.replace("...", "…")) if p.strip()]
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + len(p) + 1 > mx:
            out.append(cur); cur = p
        else:
            cur = f"{cur} {p}".strip()
    if cur:
        out.append(cur)
    return out


def _ts(t: float) -> str:
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt(ep_id: str, out: str) -> None:
    ep = S.load_episode(ep_id)
    work = C.BUILD_DIR / ep_id
    subs = ep.get("srt_replace", {})
    lines, k, t = [], 1, 0.0
    for s in ep["scenes"]:
        p = work / "audio_en" / f"{s['n']:03d}.mp3"
        d = duration(p); sil = _silences(p)
        s0 = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
        s1 = sil[-1][0] if sil and sil[-1][1] is None else d
        mids = [(a + b) / 2 for a, b in sil if b is not None and a > s0 + 0.1 and b < s1 - 0.1]
        txt = s["narration"]
        for a, b in subs.items():
            txt = txt.replace(a, b)
        cs = _chunks(txt); tot = sum(len(c) for c in cs)
        bounds, acc = [s0], 0
        for c in cs[:-1]:
            acc += len(c); est = s0 + (s1 - s0) * acc / tot
            near = min(mids, key=lambda m: abs(m - est)) if mids else est
            bounds.append(near if abs(near - est) < 1.5 and near > bounds[-1] + 0.5 else est)
        bounds.append(s1)
        for i, c in enumerate(cs):
            lines += [str(k), f"{_ts(t + bounds[i])} --> {_ts(t + bounds[i + 1])}", c, ""]; k += 1
        t += d + s.get("pad", C.BEAT_PAD)
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print(k - 1, "satır, son", round(t, 2), "sn")


def chapters(ep_id: str) -> None:
    ep = S.load_episode(ep_id); t = 0.0
    for s in ep["scenes"]:
        print(f"{int(t // 60)}:{int(t % 60):02d} {s['title']}")
        t += duration(C.BUILD_DIR / ep_id / "audio_en" / f"{s['n']:03d}.mp3") + s.get("pad", C.BEAT_PAD)
    print("toplam", round(t / 60, 2), "dk")


def thumbs(ep_id: str, a: str, b: str) -> None:
    from PIL import Image, ImageDraw, ImageFont
    font = str(C.ROOT / "brand" / "Anton.ttf")
    work = C.BUILD_DIR / ep_id; out = work / "teslim"; out.mkdir(parents=True, exist_ok=True)
    im = Image.open(work / "thumb_bg.png").convert("RGB").resize((1280, 720), Image.LANCZOS)

    def put(img, lines, size, top):
        dr = ImageDraw.Draw(img); f = ImageFont.truetype(font, size); y = top
        for t in lines:
            bb = dr.textbbox((0, 0), t, font=f)
            dr.text((1280 - 70 - (bb[2] - bb[0]) - bb[0], y - bb[1]), t, font=f, fill=(250, 244, 230),
                    stroke_width=6, stroke_fill=(20, 16, 30))
            y += bb[3] - bb[1] + 22
        return img
    im.save(out / "thumb_C_yazisiz.png")
    put(im.copy(), a.split("|"), 200 if len(a.split("|")) > 1 else 230, 120).save(out / "thumb_A.png")
    put(im.copy(), b.split("|"), 230, 200).save(out / "thumb_B.png")
    print("ok")


if __name__ == "__main__":
    cmd, *args = sys.argv[1:]
    {"rec": rec, "got": got, "voice": voice, "srt": srt, "chapters": chapters, "thumbs": thumbs}[cmd](*args)
