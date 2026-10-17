"""Montaj: klipleri indir → yavaşlat/kırp → 1080p'ye büyüt → geçişlerle birleştir → ses + müzik."""
from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor
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


def build_composite(parts: list, out: Path) -> Path:
    """Sahne klibini birden fazla üretimin parçalarından birleştirir: [[url, başla, bitir], ...]."""
    if out.exists() and out.stat().st_size > 0:
        return out
    tmp = []
    for i, (url, a, b) in enumerate(parts):
        src = download(url, out.with_name(f"{out.stem}_src{i}.mp4"))
        piece = out.with_name(f"{out.stem}_part{i}.mp4")
        _run(["ffmpeg", "-y", "-ss", f"{a:.3f}", "-to", f"{b:.3f}", "-i", str(src),
              "-vf", "scale=864:496,fps=24,format=yuv420p", "-af", "aresample=48000",
              "-c:v", "libx264", "-crf", "14", "-c:a", "aac", "-ac", "2", str(piece)])
        tmp.append(piece)
    lst = out.with_suffix(".txt")
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in tmp))
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(out)])
    return out


STILL_XFADE = 0.6  # aynı sahnedeki görseller arası geçiş (sn)
# hareket kalıpları sırayla döner: yakınlaş, sağa kaydır, uzaklaş, sola kaydır
_MOVES = [
    ("min(1+0.00045*on,1.10)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("1.10", "(iw-iw/zoom)*on/{f}", "ih/2-(ih/zoom/2)"),
    ("max(1.10-0.00045*on,1.0)", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"),
    ("1.10", "(iw-iw/zoom)*(1-on/{f})", "ih/2-(ih/zoom/2)"),
]


def build_stills(paths: list[Path], out: Path, total: float, seed: int = 0) -> Path:
    """Klipsiz sahne: görselleri yavaş yakınlaştırma/kaydırma (Ken Burns) ile canlandırır,
    aralarında yumuşak geçiş yapar. Çıktı tam `total` sn, OUT_W x OUT_H."""
    sig = "|".join(f"{p.name}:{p.stat().st_size}" for p in paths) + f"|{total:.3f}|{seed}"
    side = out.with_suffix(".json")
    if out.exists() and side.exists() and side.read_text() == sig:
        return out
    k = len(paths)
    each = (total + (k - 1) * STILL_XFADE) / k
    frames = int(round(each * C.OUT_FPS)) + 2
    ins, fc = [], []
    for i, p in enumerate(paths):
        z, x, y = _MOVES[(seed + i) % len(_MOVES)]
        ins += ["-loop", "1", "-t", f"{each + 0.2:.3f}", "-i", str(p)]
        fc.append(f"[{i}:v]scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
                  f"zoompan=z='{z}':x='{x.format(f=frames)}':y='{y.format(f=frames)}':d={frames}:"
                  f"s={C.OUT_W}x{C.OUT_H}:fps={C.OUT_FPS},trim=duration={each:.3f},setpts=PTS-STARTPTS,"
                  f"format=yuv420p[v{i}]")
    prev, off = "[v0]", 0.0
    for i in range(1, k):
        off += each - STILL_XFADE
        fc.append(f"{prev}[v{i}]xfade=transition=fade:duration={STILL_XFADE}:offset={off:.3f}[x{i}]")
        prev = f"[x{i}]"
    fc.append(f"{prev}trim=duration={total:.3f},setpts=PTS-STARTPTS[out]")
    out.parent.mkdir(parents=True, exist_ok=True)
    _run(["ffmpeg", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[out]",
          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-r", str(C.OUT_FPS), str(out)])
    side.write_text(sig)
    return out


def plan_speed(target: float, length: float = C.CLIP_SECONDS,
               min_speed: float = C.MIN_SPEED) -> tuple[float, float]:
    """(hız, donma_süresi). Klip `length` sn; hedef uzunsa yavaşlat, yetmezse son kareyi tut."""
    if target <= length:
        return 1.0, 0.0
    speed = max(length / target, min_speed)
    hold = max(0.0, target - length / speed)
    return speed, hold


def _range_args(rng) -> tuple[list[str], float]:
    """Sahnenin `clip_range` alanı: klibin sadece [başla, bitir] aralığı kullanılır."""
    if not rng:
        return [], C.CLIP_SECONDS
    a, b = rng
    return ["-ss", f"{a:.3f}", "-to", f"{b:.3f}"], b - a


def _src_len(src: Path, rng) -> tuple[list[str], float]:
    """Kesit argümanları + gerçek kaynak uzunluğu (birleşik klipler 15 sn olmayabilir)."""
    if rng:
        return _range_args(rng)
    return [], duration(src)


def render_segment(src: Path, out: Path, target: float, rng=None,
                   min_speed: float = C.MIN_SPEED) -> dict:
    cut, length = _src_len(src, rng)
    speed, hold = plan_speed(target, length, min_speed)
    sig = f"{src.name}|{src.stat().st_size}|{target:.3f}|{rng}|{min_speed}|{C.OUT_W}x{C.OUT_H}"
    side = out.with_suffix(".json")
    if out.exists() and side.exists() and side.read_text() == sig:
        return {"speed": round(speed, 3), "hold": round(hold, 2), "cached": True}
    vf = []
    if speed < 1.0:
        vf += [f"setpts=PTS/{speed:.4f}", f"minterpolate=fps={C.OUT_FPS}:mi_mode=mci:mc_mode=aobmc:vsbmc=1"]
    vf += [
        f"scale={C.OUT_W}:{C.OUT_H}:flags=lanczos",
        "unsharp=5:5:0.8:3:3:0.4",
        f"fps={C.OUT_FPS}",
        "format=yuv420p",
    ]
    # son kareyi her zaman biraz uzat: kaynak videonun görüntüsü, format süresinden (ses dahil) kısa olabilir
    vf.append(f"tpad=stop_mode=clone:stop_duration={hold + 0.4:.2f}")
    vf.append(f"trim=duration={target:.3f},setpts=PTS-STARTPTS")
    _run(["ffmpeg", "-y", *cut, "-i", str(src), "-an", "-vf", ",".join(vf),
          "-c:v", "libx264", "-preset", "medium", "-crf", "16", str(out)])
    got = duration(out)
    if got < target - 0.1:
        raise RuntimeError(f"{out.name}: segment {got:.2f} sn, beklenen {target:.2f} sn — montaj durduruldu")
    side.write_text(sig)
    return {"speed": round(speed, 3), "hold": round(hold, 2)}


def has_audio(path: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries",
                          "stream=index", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return bool(out)


def render_ambience(src: Path, out: Path, beat: float, rng=None,
                    min_speed: float = C.MIN_SPEED) -> None:
    """Klibin ortam sesini (ASMR katmanı) sahne süresine uydurur; sesi yoksa sessizlik."""
    if src is None:
        _run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo", "-t", f"{beat:.3f}", str(out)])
        return
    cut, length = _src_len(src, rng)
    speed, _ = plan_speed(beat, length, max(min_speed, 0.5))
    fade = f"afade=t=in:d=0.3,afade=t=out:st={max(beat - 0.4, 0):.2f}:d=0.4"
    if has_audio(src):
        af = f"aresample=48000,atempo={speed:.4f},apad,atrim=0:{beat:.3f},{fade}"
        cmd = ["ffmpeg", "-y", *cut, "-i", str(src), "-vn", "-af", af, "-ac", "2", str(out)]
    else:
        cmd = ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
               "-t", f"{beat:.3f}", str(out)]
    _run(cmd)


def music_bed(ep: dict, chosen: list[dict], beats: list[float], work: Path) -> Path:
    """Bölüm müzik planı (ep['music']: [{'from': sahne_no, 'track': dosya}]) → tek müzik yatağı.
    Her parça kendi bölümünün süresi kadar (gerekirse döngü) çalar, girişte/çıkışta yumuşak geçiş."""
    cues = sorted(ep["music"], key=lambda c: c["from"])
    starts, t = {}, 0.0
    for s, b in zip(chosen, beats):
        starts[s["n"]] = t
        t += b
    total = t
    parts = []
    for i, c in enumerate(cues):
        a = next((starts[n] for n in sorted(starts) if n >= c["from"]), None)
        if a is None:
            continue
        nxt = [starts[n] for n in sorted(starts) if i + 1 < len(cues) and n >= cues[i + 1]["from"]]
        b = nxt[0] if nxt else total
        if b - a < 0.5:
            continue
        d = b - a
        part = work / "music" / f"cue_{i:02d}.wav"
        part.parent.mkdir(parents=True, exist_ok=True)
        _run(["ffmpeg", "-y", "-stream_loop", "-1", "-i", str(C.MUSIC_DIR / c["track"]),
              "-t", f"{d:.3f}", "-af",
              f"aresample=48000,loudnorm=I=-20:TP=-2,afade=t=in:d=1.5,afade=t=out:st={max(d - 2.5, 0):.2f}:d=2.5",
              "-ac", "2", str(part)])
        parts.append(part)
    bed = work / "music_bed.wav"
    lst = work / "music.txt"
    lst.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
    _run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(bed)])
    return bed


def assemble(ep: dict, scenes: list[int] | None = None, music: Path | None = None,
             lang: str = "en", out_name: str | None = None) -> Path:
    work = C.BUILD_DIR / ep["id"]
    chosen = [s for s in ep["scenes"] if scenes is None or s["n"] in scenes]
    if not chosen:
        raise ValueError("Sahne seçilmedi")

    by_n = {s["n"]: s for s in ep["scenes"]}

    def clip_src(s: dict) -> Path:
        clip = asset(s, "clip")
        if clip["status"] != "done" or not clip.get("url"):
            raise RuntimeError(f"Sahne {s['n']} klibi hazır değil")
        if s.get("clip_composite"):
            return build_composite(s["clip_composite"], work / "clips" / f"{s['n']:03d}_composite.mp4")
        return download(clip["url"], work / "clips" / f"{s['n']:03d}.mp4")

    def one(i_s):
        i, s = i_s
        mp3 = work / f"audio_{lang}" / f"{s['n']:03d}.mp3"
        beat = duration(mp3) + C.BEAT_PAD
        last = i == len(chosen) - 1
        target = beat + (0 if last else XFADE)  # geçiş örtüşmesi kadar fazladan video
        seg = work / "segments" / f"{s['n']:03d}.mp4"
        seg.parent.mkdir(parents=True, exist_ok=True)
        ms = s.get("min_speed", C.MIN_SPEED)
        amb = work / "ambience" / f"{s['n']:03d}.wav"
        amb.parent.mkdir(parents=True, exist_ok=True)
        if s.get("stills"):
            # klipsiz sahne: hareketli görseller; ortam sesi başka bir sahnenin klibinden ödünç
            paths = [work / p for p in s["stills"]]
            src = build_stills(paths, work / "clips" / f"{s['n']:03d}_stills.mp4", target, seed=s["n"])
            info = render_segment(src, seg, target, None, ms)
            donor = by_n.get(s.get("ambience_from"))
            render_ambience(clip_src(donor) if donor else None, amb, beat, donor.get("clip_range") if donor else None, ms)
            return seg, (mp3, beat), amb, {"n": s["n"], "beat": round(beat, 2), "stills": len(paths), **info}
        src = clip_src(s)
        info = render_segment(src, seg, target, s.get("clip_range"), ms)
        # dudak senkronlu klibin sesi konuşma içerir → ortam katmanına alınmaz
        render_ambience(src if not s.get("no_ambience") else None, amb, beat, s.get("clip_range"), ms)
        return seg, (mp3, beat), amb, {"n": s["n"], "beat": round(beat, 2), **info}

    with ThreadPoolExecutor(max_workers=C.RENDER_WORKERS) as pool:
        results = list(pool.map(one, enumerate(chosen)))
    segs = [r[0] for r in results]
    beats = [r[1] for r in results]
    ambs = [r[2] for r in results]
    report = [r[3] for r in results]

    # --- güvenlik: her segment beklenen süre kadar mı? ---
    for k, (seg, (_, beat)) in enumerate(zip(segs, beats)):
        need = beat + (0 if k == len(segs) - 1 else XFADE)
        got = duration(seg)
        if got < need - 0.1:
            raise RuntimeError(f"{seg.name}: {got:.2f} sn < {need:.2f} sn — montaj durduruldu")

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
    bed = music_bed(ep, chosen, [b for _, b in beats], work) if ep.get("music") and not music else None
    cmd = ["ffmpeg", "-y", "-i", str(video), "-i", str(narr), "-i", str(amb_all)]
    fc = f"[2:a]volume={C.AMBIENCE_DB}dB[amb];"
    mix = "[nar][amb]"
    if bed or music:
        if bed:
            cmd += ["-i", str(bed)]
            fc += f"[3:a]volume={C.MUSIC_BED_DB}dB[m0];"
        else:
            cmd += ["-stream_loop", "-1", "-i", str(music)]
            fc += f"[3:a]volume={C.MUSIC_DB}dB,afade=t=in:d=2,afade=t=out:st={max(total - 4, 0):.2f}:d=4[m0];"
        # müzik anlatım konuşurken alçalır, cümle aralarında yükselir (ducking)
        fc += ("[1:a]asplit=2[nar][key];[m0][key]sidechaincompress=threshold=0.02:ratio=6:"
               "attack=30:release=600:makeup=1[m];")
        mix += "[m]"
    else:
        fc += "[1:a]anull[nar];"
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
