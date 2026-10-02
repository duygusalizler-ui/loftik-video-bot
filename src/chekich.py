"""
loftikayakkabi.com'daki ürünlerin gerçek malzeme/özellik bilgisi için
Chekich'in kendi perakende sitesinden (chekich.com.tr) en yakın eşleşen
ürünü arayıp GERÇEK ürün özelliklerini (malzeme, astar, topuk yüksekliği)
çeker.

NOT -- bu bir YAKLAŞIK eşleştirmedir: loftik'teki SKU (MN.../KN...) chekich'teki
(CH...) ile birebir aynı değil, loftik kendi kodlarıyla satıyor. Bu yüzden stil
kodu (CBT/CST/TBT/SBT gibi -- iki sitede de aynı kısaltmalar kullanılıyor) +
renk ile en yakın chekich ürününü buluyoruz. Bulunan malzeme/astar/topuk bilgisi
o modele ait GERÇEK bilgidir (uydurma değildir), ama bazen loftik'teki tam o
SKU ile birebir aynı olmayabilir. Yeterince iyi bir eşleşme bulunamazsa (puan 0)
fonksiyon None döner -- o zaman caption bu bilgiyi hiç kullanmaz, uydurmaz.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional
from urllib.parse import quote

from bs4 import BeautifulSoup
from curl_cffi import requests as cffi_requests

CHEKICH_BASE = "https://chekich.com.tr"

STYLE_CODE_RE = re.compile(r"\b(CBT|CST|TBT|SBT|DBT|DST|RST|GBT|CRT)\b", re.IGNORECASE)
COLOR_WORDS = [
    "SIYAH", "BEYAZ", "TABA", "VIZON", "KAHVE", "BEJ", "LACIVERT",
    "KIRMIZI", "MAVI", "HAKI", "KUM", "GRI", "YESIL", "TURUNCU", "ANTRASIT",
]

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9",
}


@dataclass
class ChekichSpecs:
    material: Optional[str] = None
    lining: Optional[str] = None
    heel_height: Optional[str] = None
    source_url: Optional[str] = None
    matched_title: Optional[str] = None


def _request(url: str):
    resp = cffi_requests.get(url, headers=HEADERS, impersonate="chrome124", timeout=20)
    resp.raise_for_status()
    return resp


def _extract_style_and_color(title: str):
    m = STYLE_CODE_RE.search(title)
    style = m.group(1).upper() if m else ""
    upper = title.upper()
    color = next((w for w in COLOR_WORDS if w in upper), "")
    return style, color


def _search_results(query: str, max_results: int = 24):
    url = f"{CHEKICH_BASE}/search?q={quote(query)}"
    soup = BeautifulSoup(_request(url).text, "html.parser")
    results = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].split("?")[0]
        if not href.startswith("/products/") or href in seen:
            continue
        title = a.get_text(strip=True)
        if not title:
            continue
        seen.add(href)
        results.append((title, CHEKICH_BASE + href))
        if len(results) >= max_results:
            break
    return results


def _score(title: str, style: str, color: str) -> int:
    t = title.upper()
    score = 0
    if style and style in t:
        score += 2
    if color and color in t:
        score += 1
    return score


def _extract_specs_from_text(text: str) -> ChekichSpecs:
    material = lining = heel = None
    m = re.search(r"Ürün Malzemesi\s*:\s*(.*?)İç Astar\s*:", text)
    if m:
        material = m.group(1).strip(" .")
    m = re.search(r"İç Astar\s*:\s*(.*?)\s*Topuk (?:Uzunluğu|Boyu)\s*:", text)
    if m:
        lining = m.group(1).strip(" .")
    m = re.search(r"Topuk (?:Uzunluğu|Boyu)\s*:\s*([\d,.]+\s*CM)", text, re.IGNORECASE)
    if m:
        heel = m.group(1).strip()
    return ChekichSpecs(material=material, lining=lining, heel_height=heel)


_CATALOG = None


def _catalog():
    """Chekich'in tum urunleri (Shopify products.json) -- bir kez cekilir."""
    global _CATALOG
    if _CATALOG is None:
        _CATALOG = []
        for page in range(1, 20):
            try:
                items = _request(f"{CHEKICH_BASE}/products.json?limit=250&page={page}").json().get("products", [])
            except Exception:  # noqa: BLE001
                break
            if not items:
                break
            _CATALOG.extend(items)
    return _CATALOG


def _exact_code_match(loftik_title: str) -> Optional[ChekichSpecs]:
    """Loftik MNxxx kodu = Chekich CHxxx kodu (ör. MN223 Alaska = CH223 Alaska).
    Ayni numara + ayni stil kodu + ayni renk varsa kesin eslesme sayilir."""
    m = re.match(r"\s*MN\s*(\d+)", loftik_title, re.IGNORECASE)
    if not m:
        return None
    num = m.group(1)
    style, color = _extract_style_and_color(loftik_title)
    candidates = [p for p in _catalog() if re.match(rf"\s*CH\s*{num}\b", p.get("title", ""), re.IGNORECASE)]
    if not candidates:
        return None
    candidates.sort(key=lambda p: _score(p["title"], style, color), reverse=True)
    best = candidates[0]
    text = re.sub(r"<[^>]+>", " ", best.get("body_html") or "")
    text = re.sub(r"\s+", " ", text)
    specs = _extract_specs_from_text(text)
    if not any([specs.material, specs.lining, specs.heel_height]):
        return None
    specs.source_url = f"{CHEKICH_BASE}/products/{best.get('handle')}"
    specs.matched_title = best["title"]
    return specs


def find_matching_specs(loftik_title: str) -> Optional[ChekichSpecs]:
    try:
        exact = _exact_code_match(loftik_title)
        if exact:
            return exact
    except Exception as exc:  # noqa: BLE001
        print(f"UYARI: Chekich kod eşleştirmesi başarısız ({exc}), aramaya geçiliyor.")
    if re.match(r"\s*MN\s*\d+", loftik_title, re.IGNORECASE):
        # MN kodlu urunun Chekich'te ayni numarasi yoksa baska bir modelle
        # eslestirip yanlis malzeme yazmaktansa bilgi eklemiyoruz.
        return None
    style, color = _extract_style_and_color(loftik_title)
    query = " ".join(filter(None, [style, "erkek ayakkabı", color])) or "erkek ayakkabı"

    results = _search_results(query)
    if not results:
        return None

    best_title, best_url = max(results, key=lambda r: _score(r[0], style, color))
    if _score(best_title, style, color) == 0:
        return None  # yeterince iyi eslesme yok -- uydurmaktansa vazgec

    soup = BeautifulSoup(_request(best_url).text, "html.parser")
    meta = soup.find("meta", attrs={"name": "description"}) or soup.find(
        "meta", attrs={"property": "og:description"}
    )
    text = meta["content"] if meta and meta.get("content") else ""

    specs = _extract_specs_from_text(text)
    if not any([specs.material, specs.lining, specs.heel_height]):
        return None

    specs.source_url = best_url
    specs.matched_title = best_title
    return specs
