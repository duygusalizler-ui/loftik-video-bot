"""
Urun sayfasindan bilgi okur (herhangi bir e-ticaret sitesi):
JSON-LD Product -> OpenGraph -> sayfa basligi sirasiyla denenir.
Gercek urun fotograflari indirilir; yapay zeka bunlari referans alir.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from urllib.parse import urljoin

import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"}


@dataclass
class Product:
    url: str
    ad: str
    fiyat: str | None = None
    aciklama: str = ""
    gorseller: list = field(default_factory=list)  # yerel dosya yollari


def _get(url: str) -> requests.Response:
    try:
        from curl_cffi import requests as creq

        r = creq.get(url, impersonate="chrome", timeout=30)
    except Exception:  # noqa: BLE001
        r = requests.get(url, headers=UA, timeout=30)
    r.raise_for_status()
    return r


def _jsonld_product(html: str) -> dict | None:
    for block in re.findall(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>', html, flags=re.S | re.I):
        try:
            data = json.loads(block.strip())
        except ValueError:
            continue
        items = data if isinstance(data, list) else data.get("@graph", [data])
        for it in items:
            if isinstance(it, dict) and "Product" in str(it.get("@type")):
                return it
    return None


def _meta(html: str, prop: str) -> str | None:
    m = re.search(rf'<meta[^>]+(?:property|name)=["\']{re.escape(prop)}["\'][^>]+content=["\']([^"\']+)', html, re.I)
    if not m:
        m = re.search(rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\']{re.escape(prop)}["\']', html, re.I)
    return m.group(1) if m else None


def fetch(url: str, out_dir: str, max_images: int = 4, extra_images: list | None = None) -> Product:
    os.makedirs(out_dir, exist_ok=True)
    html = _get(url).text
    ld = _jsonld_product(html) or {}
    ad = ld.get("name") or _meta(html, "og:title") or re.search(r"<title>(.*?)</title>", html, re.S).group(1)
    offers = ld.get("offers") or {}
    if isinstance(offers, list):
        offers = offers[0] if offers else {}
    fiyat = offers.get("price") or _meta(html, "product:price:amount")
    if not fiyat:
        m = re.search(r"(\d{1,3}(?:\.\d{3})*,\d{2})\s*(?:TL|₺)", html)
        fiyat = f"{m.group(1)} TL" if m else None
    imgs = ld.get("image") or []
    imgs = [imgs] if isinstance(imgs, str) else [i if isinstance(i, str) else i.get("url") for i in imgs]
    og = _meta(html, "og:image")
    if og:
        imgs.append(og)
    # Galeri: dosya adinda urun linkinin son parcasi (slug) gecen gorseller
    # (IdeaSoft, WooCommerce ve bircok altyapida boyle). Kucuk onizlemeler atlanir.
    slug = url.rstrip("/").split("/")[-1].split("?")[0]
    if len(slug) > 6:
        for src in re.findall(r'["\'(]([^"\'()\s]*' + re.escape(slug) + r'[^"\'()\s]*\.(?:jpe?g|png|webp))', html, re.I):
            if not re.search(r"_(min|thumb|small|xs)\.|/(thumb|small)/", src, re.I):
                imgs.append(src)
    imgs += list(extra_images or [])
    paths = []
    for src in dict.fromkeys(i for i in imgs if i):
        if len(paths) >= max_images:
            break
        src = "https:" + src if src.startswith("//") else urljoin(url, src)
        try:
            data = _get(src).content
        except Exception:  # noqa: BLE001
            continue
        if len(data) < 5000:
            continue
        p = os.path.join(out_dir, f"urun_{len(paths)}.jpg")
        with open(p, "wb") as f:
            f.write(data)
        paths.append(p)
    if not paths:
        raise RuntimeError(f"Ürün fotoğrafı bulunamadı: {url}")
    ad = re.split(r"\s+[|–-]\s+", re.sub(r"\s+", " ", ad).strip())[0]
    return Product(url=url, ad=ad, fiyat=str(fiyat) if fiyat else None,
                   aciklama=(ld.get("description") or _meta(html, "og:description") or "")[:600], gorseller=paths)
