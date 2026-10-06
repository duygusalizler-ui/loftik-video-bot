"""
Kullanim:
  python -m storyads --marka loftik --urun https://www.loftikayakkabi.com/urun/...
  python -m storyads --marka loftik --urun URL --format rovans --karakter ayı
  python -m storyads --formatlar          # formatlari listele
Cikti: cikti/<marka>/<tarih-saat>/ (video.mp4, aciklama.txt, sabit_yorum.txt, plan.json, kalite.json, kareler.jpg)
"""
import argparse
import os
from datetime import datetime

from . import brand as brand_mod
from . import pipeline
from .formats import FORMATS


def main() -> None:
    ap = argparse.ArgumentParser(prog="storyads")
    ap.add_argument("--marka")
    ap.add_argument("--urun", help="ürün sayfası linki")
    ap.add_argument("--siradaki", action="store_true",
                    help="ürünü brands/<marka>_urunler.txt listesinden sırayla seç (seri üretim)")
    ap.add_argument("--format", choices=list(FORMATS))
    ap.add_argument("--karakter")
    ap.add_argument("--gorsel", action="append", help="ek ürün fotoğrafı linki (birden çok verilebilir)")
    ap.add_argument("--cikti", default="cikti")
    ap.add_argument("--telegram", action="store_true", help="sonucu Telegram'a gönder")
    ap.add_argument("--formatlar", action="store_true")
    a = ap.parse_args()
    if a.formatlar:
        for k, v in FORMATS.items():
            print(f"{k:16} {v['ad']}: {v['fikir']}")
        return
    if not a.marka:
        ap.error("--marka gerekli")
    b = brand_mod.load(a.marka)
    if not a.urun and a.siradaki:
        from .planner import next_product
        a.urun = next_product(b)
        print(f"Sıradaki ürün: {a.urun}")
    if not a.urun:
        ap.error("--urun ya da --siradaki gerekli")
    out = os.path.join(a.cikti, b.kod, datetime.now().strftime("%Y%m%d-%H%M%S"))
    os.makedirs(out, exist_ok=True)
    res = pipeline.run(b, a.urun, out, a.format, a.karakter, a.gorsel)
    if a.siradaki:
        from .planner import remember_product
        remember_product(b, a.urun)  # basarisiz da olsa ayni urunde takilip kalmasin
    print(f"\nÇıktı klasörü: {out}")
    if res.video:
        print(f"Video: {res.video}\n--- Açıklama ---\n{res.caption}\n--- Sabit yorum ---\n{res.pinned_comment}")
    if a.telegram:
        from . import telegram

        telegram.send(res, b)
    if not res.video:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
