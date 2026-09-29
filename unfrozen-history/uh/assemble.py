"""Montaj: klipleri indir → yavaşlat/kırp → 1080p'ye büyüt → geçişlerle birleştir → ses + müzik."""
from __future__ import annotations

import subprocess
from pathlib import Path

import requests

from . import config as C
from .state import asset
from .tts import duration

XFADE = 0.5  # sahneler arası yumuşak geçiş (sn)


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)


def download(url: str, out: Path) -> Path:
    if out.exists() and out.stat().st_size > 0:
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=120) as r:
        r.raise_for_status()
        tmp = out.with_suffix(".part")
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(1 << 20):
                f.write(chunk)
        tmp.replace(out)
    return out


def plan_speed(target: float) -> tuple[float, float]:
    """(hız, donma_süresi). Klip 15 sn; hedef uzunsa yavaşlat, yetmezse son kareyi tut."""
    if target <= C.CLIP_SECONDS:
        return 1.0, 0.0
    speed = max(C.CLIP_SECONDS / target, C.MIN_SPEED)
    hold = max(0.0, target - C.CLIP_SECONDS / speed)
    return speed, hold


def render_segment(src: Path, out: Path, target: float) -> dict:
    speed, hold = plan_speed(target)
    vf = []
    if speed < 1.0:
        vf += [f"setpts=PTS/{speed:.4f}", f"minterpolate=fps={C.OUT_FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1"]
    vf += [
        f"scale={C.OUT_W}:{C.OUT_H}:flags=lanczos",
        "unsharp=5:5:0.8:3:3:0.4",
        f"fps={C.OUT_FPS}",
        "format=yuv420p",
    ]
    if hold > 0:
        vf.append(f"tpad=stop_mode=clone:stop_duration={hold + 0.1:.2f}")
    vf.append(f"trim=duration={target:.3f},setpts=PTS-STARTPTS")
    _run(["ffmpeg", "-y", "-i", str(src), "-an", "-vf", ",".join(vf),
          "-c:v", "libx264", "-preset", "medium", "-crf", "16", str(out)])
    return {"speed": round(speed, 3), "hold": round(hold, 2)}


def has_audio(path: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                          "stream=index", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return bool(out)


def render_ambience(src: Path, out: Path, beat: float) -> None:
    """Klibin ortam sesini (ASMR katmanı) sahne süresine uydurur; sesi yoksa sessizlik."""
    speed, _ = plan_speed(beat)
    fade = f"afade=t=in:d=0.3,afade=t=out:st={max(beat - 0.4, 0):.2f}:d=0.4"
    if has_audio(src):
        af = f"aresample=48000,atempo={speed:.4f},apad,atrim=0:{beat:.3f},{fade}"
        cmd = ["ffmpeg", "-y", "-i", str(src), "-vn", "-af", af, "-ac", "2", str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
               "-t", f"{beat:.3f}", str(out)]
    _run(cmd)


def assemble(ep: dict, scenes: list[int] | None = None, music: Path | None = None,
             lang: str = "en", out_name: str | None = None) -> Path:
    work = C.BUILD_DIR / ep["id"]
    chosen = [s for s in ep["scenes"] if scenes is None or s["n"] in scenes]
    if not chosen:
        raise ValueError("Sahne seçilmedi")

    segs, beats, ambs, report = [], [], [], []
    for i, s in enumerate(chosen):
        clip = asset(s, "clip")
        if clip["status"] != "done" or not clip.get("url"):
            raise RuntimeError(f"Sahne {s['n']} klibi hazır değil")
        src = download(clip["url"], work / "clips" / f"{s['n']:03d}.mp4")
        mp3 = work / f"audio_{lang}" / f"{s['n']:03d}.mp3"
        beat = duration(mp3) + C.BEAT_PAD
        last = i == len(chosen) - 1
        seg = work / "segments" / f"{s['n']:03d}.mp4"
        seg.parent.mkdir(parents=True, exist_ok=True)
        # geçiş örtüşmesi kadar fazladan video; ses zamanlaması değişmez
        info = render_segment(src, seg, beat + (0 if last else XFADE))
        amb = work / "ambience" / f"{s['n']:03d}.wav"
        amb.parent.mkdir(parents=True, exist_ok=True)
        render_ambience(src, amb, beat)
        ambs.append(amb)
        segs.append(seg)
        beats.append((mp3, beat))
        report.append({"n": s["n"], "beat": round(beat, 2), **info})

    # --- video: xfade zinciri ---
    video = work / "video_only.mp4"
    if len(segs) == 1:
        _run(["ffmpeg", "-y", "-i", str(segs[0]), "-c", "copy", str(video)])
    else:
        inputs, fc, prev, offset = [], [], "[0:v]", 0.0
        for p in segs:
            inputs += ["-i", str(p)]
        for k in range(1, len(segs)):
            offset += beats[k - 1][1]
            lbl = f"[v{k}]"
            fc.append(f"{prev}[{k}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}{lbl}")
            prev = lbl
        _run(["ffmpeg", "-y", *inputs, "-filter_complex", ";".join(fc), "-map", prev,
              "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", str(video)])

    # --- anlatım: her blok + nefes payı ---
    narr = work / f"narration_{lang}.wav"
    a_in, a_fc = [], []
    for k, (mp3, beat) in enumerate(beats):
        a_in += ["-i", str(mp3)]
        a_fc.append(f"[{k}:a]aresample=48000,apad=whole_dur={beat:.3f}[a{k}]")
    a_fc.append("".join(f"[a{k}]" for k in range(len(beats))) + f"concat=n={len(beats)}:v=0:a=1[aout]")
    _run(["ffmpeg", "-y", *a_in, "-filter_complex", ";".join(a_fc), "-map", "[aout]", str(narr)])

    # --- ortam sesi (ASMR): sahne ortam seslerini sırayla birleştir ---
    amb_all = work / "ambience.wav"
    lst = work / "ambience.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in ambs))
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(amb_all)])

    # --- final: video + anlatım + ortam sesi (+ müzik) + ses normalizasyonu ---
    total = sum(b for _, b in beats)
    out = work / (out_name or f"{ep['id']}_{lang}.mp4")
    cmd = ["ffmpeg", "-y", "-i", str(video), "-i", str(narr), "-i", str(amb_all)]
    fc = f"[2:a]volume={C.AMBIENCE_DB}dB[amb];"
    mix = "[1:a][amb]"
    if music:
        cmd += ["-stream_loop", "-1", "-i", str(music)]
        fc += f"[3:a]volume={C.MUSIC_DB}dB,afade=t=in:d=2,afade=t=out:st={max(total - 4, 0):.2f}:d=4[m];"
        mix += "[m]"
    n_in = mix.count("[")
    fc += f"{mix}amix=inputs={n_in}:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    fc += f";[0:v]fade=t=in:d=1,fade=t=out:st={max(total - 1.5, 0):.2f}:d=1.5[v]"
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{total:.3f}",
            "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]
    _run(cmd)

    for r in report:
        print(f"  sahne {r['n']:>2}: {r['beat']:5.1f} sn | hız {r['speed']} | donma {r['hold']} sn")
    print(f"Toplam: {total / 60:.1f} dk → {out}")
    return out
