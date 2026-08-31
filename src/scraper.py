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

import random
import re
import time
from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin

from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests

from . import config

# Site bir WAF/bot-koruması (ör. Cloudflare) arkasında olduğu için normal
# `requests` kütüphanesi 520 hatası alıyordu -- TLS parmak izi bot gibi
# görünüyordu. curl_cffi, gerçek bir Chrome tarayıcısının TLS parmak izini
# taklit ediyor, bu yüzden onu kullanıyoruz.
BROWSER_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}
IMPERSONATE = "chrome124"
RETRYABLE_STATUS = {429, 500, 502, 503, 504, 520, 521, 522, 523, 524}


def _request(url: str, max_attempts: int = 4):
    """Yeniden denemeli, tarayıcı-taklitli GET isteği."""
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            time.sleep(random.uniform(0.4, 1.2))  # istek deseni çok robotik olmasın
            resp = cffi_requests.get(
                url,
                headers=BROWSER_HEADERS,
                impersonate=IMPERSONATE,
                timeout=25,
            )
            if resp.status_code in RETRYABLE_STATUS:
                raise RuntimeError(f"HTTP {resp.status_code} (gecici, tekrar denenecek)")
            resp.raise_for_status()
            return resp
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            wait = attempt * 3
            print(f"  [{url}] deneme {attempt}/{max_attempts} basarisiz: {exc} -- {wait}sn sonra tekrar")
            time.sleep(wait)
    raise last_exc


def download_binary(url: str, dest_path: str) -> str:
    resp = _request(url)
    with open(dest_path, "wb") as f:
        f.write(resp.content)
    return dest_path


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
    resp = _request(url)
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


BOOT_WORD_RE = re.compile(r"\bBOT\b", re.IGNORECASE)


def _is_boot(title: str) -> bool:
    """
    Ürün BOT kategorisinde listelenmemiş olsa bile, başlığında "Bot" kelimesi
    geçiyorsa (ör. bir ürün hem "erkek-ayakkabi" hem "bot" kategorisinde
    listelenmiş olabilir) yine de eleniyor. Kategori sayfasını hariç tutmak
    tek başına yetmiyordu.
    """
    return bool(BOOT_WORD_RE.search(title))


def list_light_catalog():
    """
    Tüm izlenen kategorilerdeki ürünleri toplar (BOT kategorisi hariç).
    Bir kategori sürekli hata verirse (site geçici olarak engelliyorsa vb.)
    tüm otomasyon çökmesin diye o kategoriyi atlar, diğerlerine devam eder.
    """
    catalog = []
    for cat_url in config.CATEGORY_URLS:
        slug = category_slug_from_url(cat_url)
        if slug in config.EXCLUDED_CATEGORY_SLUGS:
            continue
        try:
            for item in list_product_urls(cat_url):
                if _is_boot(item["title"]):
                    continue
                item["category_slug"] = slug
                catalog.append(item)
        except Exception as exc:  # noqa: BLE001
            print(f"UYARI: {cat_url} taranamadi, atlaniyor. Hata: {exc}")
            continue
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

    # Aynı fotoğraf sitede hem tam boyut ("...-731.jpg") hem küçük/thumbnail
    # ("...-731_min.jpg") olarak iki ayrı <img> etiketinde geçebiliyor.
    # Bunları AYNI fotoğraf sayıp tekilleştiriyoruz (yoksa carousel'de aynı
    # görsel iki kez -- biri büyük biri küçük boy -- çıkıyordu), ve tercihen
    # tam boyutlu (kalitesi daha iyi) versiyonu kullanıyoruz.
    gallery = []
    seen_keys = set()
    for img in soup.find_all("img"):
        src = img.get("src") or ""
        if "/myassets/products/" not in src:
            continue
        clean_src = src.split("?")[0]
        key = re.sub(r"_min(\.\w+)$", r"\1", clean_src)  # tekillestirme anahtari
        if key in seen_keys:
            continue
        seen_keys.add(key)
        full_src = clean_src.replace("_min.", ".", 1) if "_min." in clean_src else clean_src
        gallery.append(full_src)

    if main_image:
        main_key = re.sub(r"_min(\.\w+)$", r"\1", main_image)
        if main_key not in seen_keys:
            gallery.insert(0, main_image)
            seen_keys.add(main_key)

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
