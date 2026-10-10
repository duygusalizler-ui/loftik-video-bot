"""İkinci dil ses kanalı (YouTube çok dilli ses): videoyu değiştirmeden, çeviri anlatımı
İngilizce sahne zamanlamasına oturtur; ortam sesi + müzik yatağı aynı kalır."""
from __future__ import annotations

import json
from pathlib import Path

from . import config as C
from .assemble import _run, duration

GAP = 0.3        # iki sahne arasında en az nefes
MAX_TEMPO = 1.14  # en fazla bu kadar hızlandır (doğal kalsın)


def plan(ep: dict, lang: str) -> list[dict]:
    work = C.BUILD_DIR / ep["id"]
    t, end, rows = 0.0, 0.0, []
    for s in ep["scenes"]:
        n = s["n"]
        beat = duration(work / "audio_eleven" / f"{n:03d}.mp3") + C.BEAT_PAD
        raw = work / f"audio_{lang}_raw" / f"{n:03d}.mp3"
        d = duration(raw)
        start = max(t, end + GAP)
        avail = t + beat - 0.15 - start
        tempo = min(max(1.06, d / avail if avail > 0 else MAX_TEMPO), MAX_TEMPO)
        end = start + d / tempo
        rows.append({"n": n, "scene_start": t, "start": start, "end": end, "tempo": tempo, "lag": end - (t + beat)})
        t += beat
    return rows


def srt_time(x: float) -> str:
    ms = int(round(x * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def srt(rows: list[dict], texts: dict, out: Path, max_chars: int = 84) -> None:
    """Her sahne metnini cümlelere böler, sahne süresine karakter oranıyla yayar."""
    import re
    lines, k = [], 1
    for r in rows:
        txt = re.sub(r"\b[A-ZÁÉÍÓÚÑ]{2,}\b", lambda m: m.group(0).lower(), texts[str(r["n"])].replace("...", "…"))
        txt = re.sub(r"(^|[.!?]\s+[¡¿]?)([a-záéíóúñ])", lambda m: m.group(1) + m.group(2).upper(), txt)
        parts = [p.strip() for p in re.split(r"(?<=[.!?…])\s+", txt) if p.strip()]
        chunks, cur = [], ""
        for p in parts:
            if cur and len(cur) + len(p) + 1 > max_chars:
                chunks.append(cur); cur = p
            else:
                cur = f"{cur} {p}".strip()
        if cur:
            chunks.append(cur)
        total = sum(len(c) for c in chunks)
        a = r["start"]
        for c in chunks:
            b = a + (r["end"] - r["start"]) * len(c) / total
            lines += [str(k), f"{srt_time(a)} --> {srt_time(b)}", c, ""]
            k += 1
            a = b
    out.write_text("\n".join(lines), encoding="utf-8")


def build(ep: dict, lang: str, texts: dict) -> Path:
    work = C.BUILD_DIR / ep["id"]
    rows = plan(ep, lang)
    # zincirdeki atempo'yu çıkar, sahne bazlı tempo ile değiştir (atempo her zaman başta olmayabilir)
    post = ",".join(f for f in ep["voice_engine"]["post"].split(",") if not f.startswith("atempo="))
    proc = work / f"audio_{lang}"
    proc.mkdir(exist_ok=True)
    ins, fc = [], []
    for i, r in enumerate(rows):
        src = work / f"audio_{lang}_raw" / f"{r['n']:03d}.mp3"
        dst = proc / f"{r['n']:03d}.wav"
        _run(["ffmpeg", "-y", "-i", str(src), "-af", f"atempo={r['tempo']:.4f},{post}", "-ar", "48000", "-ac", "1", str(dst)])
        ins += ["-i", str(dst)]
        ms = int(r["start"] * 1000)
        fc.append(f"[{i}:a]adelay={ms}|{ms}[d{i}]")
    total = duration(work / "ambience.wav")
    narr = work / f"narration_{lang}.wav"
    fc.append("".join(f"[d{i}]" for i in range(len(rows))) +
              f"amix=inputs={len(rows)}:duration=longest:normalize=0,apad=whole_dur={total:.3f}[n]")
    _run(["ffmpeg", "-y", *ins, "-filter_complex", ";".join(fc), "-map", "[n]", "-ac", "1", str(narr)])
    # final ses: anlatım + ortam + müzik (ducking) — video render'ıyla aynı zincir
    out = work / f"{ep['id']}_audio_{lang}.m4a"
    fc = (f"[1:a]volume={C.AMBIENCE_DB}dB[amb];[2:a]volume={C.MUSIC_BED_DB}dB[m0];"
          "[0:a]asplit=2[nar][key];[m0][key]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=600:makeup=1[m];"
          "[nar][amb][m]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11,"
          f"afade=t=out:st={total - 1.5:.2f}:d=1.5[a]")
    _run(["ffmpeg", "-y", "-i", str(narr), "-i", str(work / "ambience.wav"), "-i", str(work / "music_bed.wav"),
          "-filter_complex", fc, "-map", "[a]", "-t", f"{total:.3f}", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", str(out)])
    srt(rows, texts, work / f"{ep['id']}_{lang}.srt")
    (work / f"dub_{lang}_plan.json").write_text(json.dumps(rows, indent=1))
    return out
