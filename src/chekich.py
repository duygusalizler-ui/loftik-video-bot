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
    m = re.search(r"İç Astar\s*:\s*(.*?)Topuk Uzunluğu\s*:", text)
    if m:
        lining = m.group(1).strip(" .")
    m = re.search(r"Topuk Uzunluğu\s*:\s*([\d,.]+\s*CM)", text, re.IGNORECASE)
    if m:
        heel = m.group(1).strip()
    return ChekichSpecs(material=material, lining=lining, heel_height=heel)


def find_matching_specs(loftik_title: str) -> Optional[ChekichSpecs]:
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
