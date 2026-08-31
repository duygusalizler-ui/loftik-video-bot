"""
Remotion (Node.js/React tabanli, kod ile video olusturan bir sistem) ile
video uretir. AI DEGIL -- gercek urun fotograflarini kod ile (yakinlasma,
gecis, metin animasyonu) hareketlendirir. Bu yuzden urun tasarimi/logo/
renk ASLA degismez -- hallucination riski matematiksel olarak sifir,
cunku hicbir goruntu "uretilmiyor", sadece gercek fotograflar animasyonlu
sekilde gosteriliyor.

Gereksinim: remotion/ klasorunde `npm install` calistirilmis olmali
(GitHub Actions workflow'u bunu otomatik yapiyor).
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

REMOTION_DIR = Path(__file__).resolve().parent.parent / "remotion"
ASSETS_DIR = REMOTION_DIR / "public" / "assets"


def _prepare_assets(image_paths: list) -> list:
    """Gercek urun fotograflarini Remotion'un public/assets klasorune kopyalar."""
    if ASSETS_DIR.exists():
        shutil.rmtree(ASSETS_DIR)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)

    relative_paths = []
    for i, src_path in enumerate(image_paths):
        ext = Path(src_path).suffix or ".jpg"
        dest_name = f"img{i}{ext}"
        shutil.copy(src_path, ASSETS_DIR / dest_name)
        relative_paths.append(f"assets/{dest_name}")
    return relative_paths


def generate_product_video(
    image_paths: list,
    title: str,
    brand: str,
    price_text,
    output_path: str,
) -> str:
    """
    image_paths: yerel diskteki gercek urun fotograflarinin yollari (indirilmis).
    output_path: cikti mp4'unun kaydedilecegi yol.
    """
    relative_assets = _prepare_assets(image_paths)

    props = {
        "title": title,
        "brand": brand or "LOFTİK AYAKKABI",
        "priceText": str(price_text) if price_text else "",
        "images": relative_assets,
    }
    props_path = REMOTION_DIR / "render_props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")

    out_abs = str(Path(output_path).resolve())

    cmd = [
        "npx",
        "remotion",
        "render",
        "src/index.ts",
        "ProductVideo",
        out_abs,
        "--props=render_props.json",
        "--log=error",
    ]
    result = subprocess.run(
        cmd,
        cwd=str(REMOTION_DIR),
        capture_output=True,
        text=True,
        timeout=300,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Remotion render basarisiz (exit {result.returncode}):\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}"
        )

    if not Path(out_abs).exists():
        raise RuntimeError("Remotion render 'basarili' dedi ama cikti dosyasi bulunamadi.")

    return out_abs
