"""
loftikayakkabi.com için basit bir ürün scraper'ı.

Site IdeaSoft alt yapısını kullanıyor. Bu dosya iki katmanlı çalışır:

1) list_light_catalog() -> kategori listeleme sayfalarını gezer, sadece
   ürün linki + başlığı toplar (hafif, her seferinde tüm ürün detay
   sayfalarını çekmez).
2) fetch_product(url) -> SEÇİLEN tek ürünün detay sayfasını açar,
   galeri görselleri / marka / fiyat gibi bilgileri çıkarır.

Böylece her otomasyon çalışmasında siteye sadece birkaç kategori sayfası +
1 ürün detay sayfası isteği gider (siteyi yormamak için).

NOT: Bu scraper, sitenin Ağustos 2026'daki HTML yapısına göre yazıldı.
Site teması/şablonu değişirse seçicileri güncellemek gerekebilir.
Hızlıca test etmek için: `python -m src.scraper`
"""
from __future__ import annotations

import re
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from . import config

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; LoftikVideoBot/1.0)"
}


@dataclass
class Product:
    url: str
    slug: str
    title: str
    category_slug: Optional[str] = None
    brand: Optional[str] = None
    price_text: Optional[str] = None
    main_image: Optional[str] = None
    gallery_images: list = field(default_factory=list)


def _get_soup(url: str) -> BeautifulSoup:
    resp = requests.get(url, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, "html.parser")


def category_slug_from_url(category_url: str) -> str:
    return category_url.rstrip("/").split("/")[-1]


def list_product_urls(category_url: str, max_pages: int = 20):
    """Bir kategorideki tüm sayfaları gezip (url, başlık) çiftlerini döner."""
    results = []
    seen = set()
    for page in range(1, max_pages + 1):
        page_url = category_url if page == 1 else f"{category_url}?page={page}"
        soup = _get_soup(page_url)
        found_this_page = 0
        for a in soup.find_all("a", href=True):
            href = a["href"].split("?")[0]
            if not href.startswith("/urun/"):
                continue
            full_url = urljoin(config.SITE_BASE_URL, href)
            if full_url in seen:
                continue
            title = (a.get("title") or a.get_text(strip=True)).strip()
            if not title:
                continue
            seen.add(full_url)
            results.append({"url": full_url, "title": title})
            found_this_page += 1
        if found_this_page == 0:
            break
        time.sleep(0.4)
    return results


def list_light_catalog():
    """Tüm izlenen kategorilerdeki ürünleri toplar (BOT kategorisi hariç)."""
    catalog = []
    for cat_url in config.CATEGORY_URLS:
        slug = category_slug_from_url(cat_url)
        if slug in config.EXCLUDED_CATEGORY_SLUGS:
            continue
        for item in list_product_urls(cat_url):
            item["category_slug"] = slug
            catalog.append(item)
    return catalog


def fetch_product(url: str, category_slug: Optional[str] = None) -> Product:
    soup = _get_soup(url)

    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else url

    slug = url.rstrip("/").split("/")[-1]

    brand = None
    brand_link = soup.find("a", href=re.compile(r"^/marka/"))
    if brand_link:
        brand = brand_link.get_text(strip=True)

    og_image_tag = soup.find("meta", attrs={"property": "og:image"})
    main_image = None
    if og_image_tag and og_image_tag.get("content"):
        main_image = og_image_tag["content"].split("?")[0]

    gallery = []
    for img in soup.find_all("img"):
        src = img.get("src") or ""
        if "/myassets/products/" in src:
            gallery.append(src.split("?")[0])
    gallery = list(dict.fromkeys(gallery))  # sıralı unique
    if main_image and main_image not in gallery:
        gallery.insert(0, main_image)

    price_text = None
    price_match = re.search(r"[\d.]+,\d{2}\s*TL", soup.get_text())
    if price_match:
        price_text = price_match.group(0)

    return Product(
        url=url,
        slug=slug,
        title=title,
        category_slug=category_slug,
        brand=brand,
        price_text=price_text,
        main_image=main_image,
        gallery_images=gallery[:4],
    )


if __name__ == "__main__":
    # Dry-run: siteyi kontrol etmek için `python -m src.scraper`
    test_cat = config.CATEGORY_URLS[0]
    found = list_product_urls(test_cat, max_pages=1)
    print(f"{test_cat} -> ilk sayfada {len(found)} ürün linki bulundu")
    if found:
        p = fetch_product(found[0]["url"])
        print("Örnek ürün:", p)
