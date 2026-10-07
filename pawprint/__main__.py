"""PawPrint Globe — stok + ürün Reel üretici.

Akış:
  1. themes.json'dan son kullanılmayan tema seçilir.
  2. Pexels'ten o temaya uygun, daha önce kullanılmamış dikey stok klipler indirilir.
  3. Stok klipler (duygusal açılış) + bizim ürün sahnemiz tek video olarak birleştirilir.
  4. Gemini ile İngilizce açıklama + Türkçe çevirisi yazılır (Gemini yoksa hazır şablon).
  5. Video + açıklama Telegram'a gönderilir. Paylaşımı kullanıcı onaylayıp kendisi yapar.

Çalıştırma:  python -m pawprint            (Telegram'a gönderir)
             python -m pawprint --yerel    (sadece pawprint/cikti/ altına yazar)
             python -m pawprint --tema paws --yazi
"""
from __future__ import annotations

import argparse
import json
import os
import random
import subprocess
import sys
import textwrap
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
ASSETS = ROOT / "assets" / "product"
STATE_FILE = ROOT / "data" / "used.json"
OUT_DIR = ROOT / "cikti"
THEMES = json.loads((ROOT / "themes.json").read_text(encoding="utf-8"))["themes"]

STORE_URL = os.environ.get("PAWPRINT_STORE_URL", "https://pawprintglobe.wed2c.com")
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
TG_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
TG_CHAT = os.environ.get("PAWPRINT_TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID", "")

W, H, FPS = 1080, 1920, 24
STOCK_CLIPS = 3
STOCK_SECONDS = 2.4
FADE = 0.35
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ----------------------------------------------------------------- yardımcılar
def run(cmd: list[str]) -> None:
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-3000:])
        raise RuntimeError(f"Komut başarısız: {' '.join(cmd[:4])} ...")


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
        capture_output=True, text=True, check=True,
    ).stdout.strip()
    return float(out)


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"pexels_ids": [], "themes": [], "runs": []}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    state["pexels_ids"] = state["pexels_ids"][-2000:]
    state["themes"] = state["themes"][-20:]
    state["runs"] = state["runs"][-200:]
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def pick_theme(state: dict, forced: str | None) -> dict:
    if forced:
        for t in THEMES:
            if t["id"] == forced:
                return t
        raise SystemExit(f"Tema bulunamadı: {forced}. Seçenekler: {[t['id'] for t in THEMES]}")
    recent = state["themes"][-(len(THEMES) - 1):] if len(THEMES) > 1 else []
    pool = [t for t in THEMES if t["id"] not in recent] or THEMES
    return random.choice(pool)


# ----------------------------------------------------------------- Pexels
def pexels_search(query: str) -> list[dict]:
    if not PEXELS_KEY:
        raise RuntimeError("PEXELS_API_KEY tanımlı değil (GitHub Secrets'a ekle).")
    r = requests.get(
        "https://api.pexels.com/videos/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "orientation": "portrait", "size": "medium", "per_page": 40},
        timeout=60,
    )
    r.raise_for_status()
    return r.json().get("videos", [])


def best_file(video: dict) -> dict | None:
    files = [
        f for f in video.get("video_files", [])
        if f.get("file_type") == "video/mp4" and f.get("height") and f.get("width")
        and f["height"] > f["width"] and f["height"] >= 1280
    ]
    if not files:
        return None
    # 1920'ye en yakın olanı al (4K dosyaları gereksiz büyük).
    return min(files, key=lambda f: abs(f["height"] - 1920))


def fetch_stock(theme: dict, state: dict, workdir: Path) -> list[dict]:
    used = set(state["pexels_ids"])
    chosen: list[dict] = []
    queries = list(theme["queries"])
    for q in queries * 2:  # her sorgudan önce 1, yetmezse 2. tur
        if len(chosen) >= STOCK_CLIPS:
            break
        candidates = []
        for v in pexels_search(q):
            if v["id"] in used or any(c["id"] == v["id"] for c in chosen):
                continue
            if v.get("duration", 0) < STOCK_SECONDS + 1.5:
                continue
            f = best_file(v)
            if f:
                candidates.append((v, f))
        if not candidates:
            continue
        v, f = random.choice(candidates[:12])
        path = workdir / f"stock_{v['id']}.mp4"
        with requests.get(f["link"], stream=True, timeout=180) as resp:
            resp.raise_for_status()
            with open(path, "wb") as fh:
                for chunk in resp.iter_content(1 << 20):
                    fh.write(chunk)
        chosen.append({"id": v["id"], "path": path, "query": q, "url": v.get("url"), "dur": v.get("duration", 0)})
        print(f"Stok: {q!r} -> {v['id']} ({f['width']}x{f['height']})")
    if len(chosen) < 2:
        raise RuntimeError("Yeterli stok klip bulunamadı.")
    return chosen


# ----------------------------------------------------------------- kurgu
def build_video(stock: list[dict], theme: dict, with_text: bool, out: Path) -> None:
    product = ASSETS / f"{theme['product']}.mp4"
    inputs: list[str] = []
    for s in stock:
        start = max(0.5, min(s["dur"] * 0.3, s["dur"] - STOCK_SECONDS - 0.5))
        inputs += ["-ss", f"{start:.2f}", "-t", f"{STOCK_SECONDS + FADE:.2f}", "-i", str(s["path"])]
    inputs += ["-i", str(product)]
    n = len(stock)
    seg_len = STOCK_SECONDS + FADE
    grade = "eq=saturation=0.95:contrast=1.03,colorbalance=rs=0.04:gs=0.01:bs=-0.04:rm=0.03:bm=-0.03"

    parts = []
    for i in range(n):
        parts.append(
            f"[{i}:v]scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},"
            f"fps={FPS},{grade},setsar=1,format=yuv420p,trim=0:{seg_len:.3f},setpts=PTS-STARTPTS,settb=1/{FPS}[s{i}]"
        )
    parts.append(f"[{n}:v]scale={W}:{H},fps={FPS},setsar=1,format=yuv420p,setpts=PTS-STARTPTS,settb=1/{FPS}[p]")

    # xfade zinciri
    labels = [f"s{i}" for i in range(n)] + ["p"]
    cur, cur_len = labels[0], seg_len
    for i, nxt in enumerate(labels[1:], start=1):
        offset = cur_len - FADE
        outl = f"x{i}"
        parts.append(f"[{cur}][{nxt}]xfade=transition=fade:duration={FADE}:offset={offset:.3f}[{outl}]")
        nxt_len = seg_len if nxt != "p" else duration(product)
        cur, cur_len = outl, offset + nxt_len
    product_start = seg_len * n - FADE * n

    vout = cur
    if with_text:
        txt_file = out.parent / "hook.txt"
        txt_file.write_text("\n".join(textwrap.wrap(theme["hook_en"], 24)), encoding="utf-8")
        parts.append(
            f"[{cur}]drawtext=fontfile={FONT}:textfile='{txt_file}':fontcolor=white:fontsize=64:"
            f"line_spacing=14:x=(w-text_w)/2:y=h*0.16:box=1:boxcolor=black@0.35:boxborderw=28:"
            f"enable='between(t,0.2,{product_start:.2f})'[vt]"
        )
        vout = "vt"

    # ses: stok kısmı sessiz, ürün sahnesinin doğal sesleri (kil, nefes, kapak tıkı)
    ms = int(product_start * 1000)
    parts.append(f"[{n}:a]aresample=48000,adelay={ms}|{ms},afade=t=in:st={product_start:.2f}:d=0.4,apad[a]")

    total = cur_len
    cmd = ["ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", ";".join(parts),
           "-map", f"[{vout}]", "-map", "[a]", "-t", f"{total:.3f}",
           "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-maxrate", "14M", "-bufsize", "28M",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(out)]
    run(cmd)


def contact_sheet(video: Path, out: Path) -> None:
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", "fps=1,scale=180:-1,tile=6x3",
         "-frames:v", "1", str(out)])


# ----------------------------------------------------------------- açıklama
FALLBACK_CAPTIONS = [
    ("{hook}\n\nPress their paw into soft clay, close the crystal dome, and keep it on your shelf forever. "
     "A tiny globe that holds the biggest love. 🐾\n\nLink in bio 🔗\n\n"
     "#dogsofinstagram #petmemorial #dogmom #pawprint #seniordog #goldenretriever #petkeepsake #rainbowbridge",
     "{hook_tr}\n\nPatisini yumuşak kile bastır, kristal kubbeyi kapat ve sonsuza kadar rafında sakla. "
     "En büyük sevgiyi taşıyan küçük bir küre. 🐾\n\nLink bio'da 🔗"),
    ("{hook}\n\nWe made his paw print keepsake at home in 2 minutes. Now he's with me every single day. 🤍\n\n"
     "Get yours — link in bio 🐾\n\n#dogsofinstagram #dogdad #pawprintkeepsake #seniordogsofinstagram #doglover #petloss",
     "{hook_tr}\n\nPati izi anı küremizi evde 2 dakikada yaptık. Artık her gün yanımda. 🤍\n\n"
     "Seninkini al — link bio'da 🐾"),
]


def write_caption(theme: dict) -> tuple[str, str]:
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        try:
            from google import genai
            from google.genai import types
            sys.path.insert(0, str(ROOT.parent))
            from src.gemini_util import generate_content

            prompt = (
                "You write Instagram Reel captions for PawPrint Globe, a DIY pet paw print clay keepsake "
                "inside a clear crystal dome (US audience, dog/cat owners). Tone: warm, emotional, honest, no "
                "exaggerated or medical claims, no fake reviews or fake personal stories presented as real customer "
                "testimony. The video opens with emotional dog moments, then shows pressing a paw into clay and "
                f"closing the dome. Hook line: \"{theme['hook_en']}\".\n"
                "Write: 1 hook line, 1-2 short sentences, a CTA 'Link in bio', then 6-9 relevant hashtags. "
                "Max 600 characters. Also give a natural Turkish translation of the whole caption (without hashtags). "
                'Return JSON: {"en": "...", "tr": "..."}'
            )
            client = genai.Client(api_key=key)
            resp = generate_content(client, prompt, types.GenerateContentConfig(
                response_mime_type="application/json", temperature=0.9))
            data = json.loads(resp.text)
            if data.get("en") and data.get("tr"):
                return data["en"].strip(), data["tr"].strip()
        except Exception as exc:  # noqa: BLE001
            print(f"UYARI: Gemini açıklaması yazılamadı, şablon kullanılıyor: {exc}")
    en, tr = random.choice(FALLBACK_CAPTIONS)
    return en.format(hook=theme["hook_en"]), tr.format(hook_tr=theme["hook_tr"])


# ----------------------------------------------------------------- Telegram
def tg_chat_id() -> str:
    if TG_CHAT:
        return TG_CHAT
    # Chat ID girilmemişse: bota en son "Start" yazan sohbeti bul.
    r = requests.get(f"https://api.telegram.org/bot{TG_TOKEN}/getUpdates", timeout=30).json()
    for upd in reversed(r.get("result", [])):
        msg = upd.get("message") or upd.get("my_chat_member") or {}
        chat = msg.get("chat")
        if chat:
            print(f"Telegram chat id bulundu: {chat['id']} (PAWPRINT_TELEGRAM_CHAT_ID olarak kaydedebilirsin)")
            return str(chat["id"])
    raise RuntimeError("Telegram chat bulunamadı: Telegram'da botu açıp Start'a bas.")


def tg_send(video: Path, sheet: Path, caption_en: str, caption_tr: str, theme: dict) -> None:
    if not TG_TOKEN:
        raise RuntimeError("TELEGRAM_BOT_TOKEN tanımlı değil.")
    chat = tg_chat_id()
    base = f"https://api.telegram.org/bot{TG_TOKEN}"
    with open(video, "rb") as fh:
        requests.post(f"{base}/sendVideo", data={"chat_id": chat, "caption": caption_en[:1024],
                                                  "supports_streaming": True},
                      files={"video": fh}, timeout=300).raise_for_status()
    note = (
        "🐾 PawPrint Globe — yeni Reel hazır\n\n"
        f"Tema: {theme['id']}\n\n"
        f"🇹🇷 Açıklamanın Türkçesi:\n{caption_tr}\n\n"
        "Paylaşmadan önce:\n"
        "• Instagram'da trend olan duygusal bir müzik ekle (piyano / acoustic).\n"
        "• Ayarlar → 'AI ile oluşturuldu' etiketini aç (ürün sahnesi yapay zeka).\n"
        "• Açıklamayı yukarıdaki videodan kopyala (İngilizce).\n"
        f"• Bio linki: {STORE_URL}"
    )
    requests.post(f"{base}/sendMessage", data={"chat_id": chat, "text": note[:4000]}, timeout=60).raise_for_status()
    if sheet.exists():
        with open(sheet, "rb") as fh:
            requests.post(f"{base}/sendPhoto", data={"chat_id": chat, "caption": "Kare önizleme"},
                          files={"photo": fh}, timeout=60)


# ----------------------------------------------------------------- ana akış
def main() -> None:
    ap = argparse.ArgumentParser(prog="pawprint")
    ap.add_argument("--tema", help="Tema id (boş = otomatik)")
    ap.add_argument("--yazi", action="store_true", help="Açılışa kanca yazısı ekle")
    ap.add_argument("--yerel", action="store_true", help="Telegram'a gönderme")
    ap.add_argument("--adet", type=int, default=1, help="Kaç video üretilsin")
    args = ap.parse_args()

    state = load_state()
    for k in range(args.adet):
        theme = pick_theme(state, args.tema)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        work = OUT_DIR / f"{stamp}_{theme['id']}"
        work.mkdir(parents=True, exist_ok=True)
        print(f"== Video {k + 1}/{args.adet}: tema {theme['id']}")

        stock = fetch_stock(theme, state, work)
        video = work / "reel.mp4"
        build_video(stock, theme, args.yazi, video)
        sheet = work / "kareler.jpg"
        contact_sheet(video, sheet)
        en, tr = write_caption(theme)
        (work / "aciklama_en.txt").write_text(en, encoding="utf-8")
        (work / "aciklama_tr.txt").write_text(tr, encoding="utf-8")
        print(f"Hazır: {video} ({duration(video):.1f} sn, {video.stat().st_size / 1e6:.1f} MB)")

        if not args.yerel:
            tg_send(video, sheet, en, tr, theme)
            print("Telegram'a gönderildi.")

        state["pexels_ids"] += [s["id"] for s in stock]
        state["themes"].append(theme["id"])
        state["runs"].append({"at": stamp, "theme": theme["id"], "stock": [s["url"] for s in stock]})
        save_state(state)
        for s in stock:
            s["path"].unlink(missing_ok=True)
        time.sleep(1)


if __name__ == "__main__":
    main()
