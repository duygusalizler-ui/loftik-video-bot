"""
Rakip reklam analizi -- HER icerik uretiminden once calisir.

1) Urune gore anahtar kelimeler cikarilir (ör. "chelsea bot", "erkek bot").
2) Meta Reklam Kutuphanesi (Ad Library) Apify uzerinden taranir; Turkiye'de
   su an yayinda olan rakip reklamlar toplanir.
3) En uzun suredir yayinda olan reklamlar "kazanan" sayilir (bir reklam
   haftalarca yayinda kaliyorsa para kazandiriyordur).
4) Gemini bu reklamlari (metin + onizleme gorselleri) analiz eder ve bizim
   videomuz icin bir "brief" cikarir: kanca cumlesi, sahneler, ekran yazilari,
   paylasim metni.

APIFY_TOKEN yoksa ya da tarama basarisiz olursa: Gemini, Google aramasiyla
guncel rakip reklam trendlerini arastirip yine brief cikarir. O da olmazsa
guvenli bir varsayilan brief doner -- otomasyon asla burada durmaz.

Rapor data/rakip_raporlari/ altina JSON olarak kaydedilir (GitHub'da gecmisi
gorulebilsin diye workflow bunu da commit'ler).
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from urllib.parse import quote

import requests

from . import config

APIFY_RUN_URL = "https://api.apify.com/v2/acts/{actor}/run-sync-get-dataset-items"

# Sahne kurallari -- kullanici geri bildirimi: dogal yurume/kombin sahneleri
# iyi sonuc veriyor, su sicramasi gibi hizli/efektli aksiyonlar bozuk cikiyor.
SCENE_RULES = (
    "Scenes must be calm, natural and realistic: walking on a street, standing, "
    "leaning on a wall, sitting on steps, stepping out of a car, walking in a "
    "cafe street, etc. The product must be clearly visible and large in frame. "
    "AVOID fast action or effects: no water splashes, no jumping, no running, "
    "no slow-motion stunts, no close-ups of hands touching the shoe, no mirrors."
)


# ---------------------------------------------------------------------------
# Anahtar kelimeler
# ---------------------------------------------------------------------------
def keywords_for(title: str, category_slug: str | None, is_boot: bool) -> list[str]:
    t = title.lower()
    kws: list[str] = []
    male = "erkek" in t or category_slug == "erkek-ayakkabi"
    female = "kadın" in t or "kadin" in t or category_slug == "kadin-ayakkabi"
    if is_boot or " bot" in f" {t}":
        if "chelsea" in t or "alaska" in t or "yukon" in t or "bryggen" in t:
            kws.append("chelsea bot")
        kws.append("erkek bot" if male else ("kadın bot" if female else "bot ayakkabı"))
        kws.append("deri bot")
    elif "topuk" in t:
        kws += ["kadın topuklu ayakkabı", "topuklu ayakkabı"]
    elif "spor" in t or "sneaker" in t or "runner" in t or category_slug == "spor-ayakkabi":
        kws += ["erkek spor ayakkabı" if male else "spor ayakkabı", "sneaker"]
    else:
        kws.append("erkek ayakkabı" if male else ("kadın ayakkabı" if female else "ayakkabı"))
    kws += config.COMPETITOR_PAGES
    # tekrarlari at, sirayi koru
    return list(dict.fromkeys(kws))[:4]


# ---------------------------------------------------------------------------
# Apify ile Meta Ad Library taramasi
# ---------------------------------------------------------------------------
def _ad_library_url(keyword: str) -> str:
    return (
        "https://www.facebook.com/ads/library/?active_status=active&ad_type=all"
        f"&country={config.AD_LIBRARY_COUNTRY}&q={quote(keyword)}"
        "&search_type=keyword_unordered&media_type=all"
    )


def _dig(obj, *keys):
    """Ic ice dict/list'te ilk bulunan anahtari dondurur (actor ciktisi degisebilir)."""
    if isinstance(obj, dict):
        for k in keys:
            if k in obj and obj[k] not in (None, "", [], {}):
                return obj[k]
        for v in obj.values():
            found = _dig(v, *keys)
            if found not in (None, "", [], {}):
                return found
    elif isinstance(obj, list):
        for v in obj:
            found = _dig(v, *keys)
            if found not in (None, "", [], {}):
                return found
    return None


def _parse_date(value) -> datetime | None:
    if value is None:
        return None
    try:
        if isinstance(value, (int, float)):
            return datetime.fromtimestamp(value, tz=timezone.utc)
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (ValueError, OSError):
        return None


def _normalize(raw: dict, keyword: str) -> dict | None:
    text = _dig(raw, "body", "text", "adText", "ad_creative_body")
    if isinstance(text, dict):
        text = text.get("text")
    page = _dig(raw, "pageName", "page_name")
    start = _parse_date(_dig(raw, "startDate", "start_date", "adDeliveryStartTime", "startDateFormatted"))
    days = (datetime.now(timezone.utc) - start).days if start else None
    video = _dig(raw, "videoHdUrl", "videoSdUrl", "video_hd_url", "video_sd_url")
    preview = _dig(raw, "videoPreviewImageUrl", "originalImageUrl", "resizedImageUrl", "imageUrl")
    if not (text or video or preview):
        return None
    return {
        "keyword": keyword,
        "page": page,
        "text": (str(text) if text else "")[:600],
        "title": _dig(raw, "title", "linkTitle"),
        "cta": _dig(raw, "ctaText", "cta_text"),
        "days_running": days,
        "format": "video" if video else "gorsel",
        "preview_image": preview,
        "library_id": _dig(raw, "adArchiveID", "adArchiveId", "ad_archive_id", "id"),
    }


def fetch_competitor_ads(keywords: list[str]) -> list[dict]:
    if not config.APIFY_TOKEN:
        raise RuntimeError("APIFY_TOKEN tanımlı değil")
    ads: list[dict] = []
    for kw in keywords:
        resp = requests.post(
            APIFY_RUN_URL.format(actor=config.APIFY_ADS_ACTOR),
            params={"token": config.APIFY_TOKEN, "timeout": 240},
            json={
                "startUrls": [{"url": _ad_library_url(kw)}],
                "resultsLimit": config.COMPETITOR_ADS_PER_KEYWORD,
            },
            timeout=300,
        )
        if resp.status_code >= 400:
            print(f"UYARI: Apify '{kw}' taramasi basarisiz ({resp.status_code}): {resp.text[:200]}")
            continue
        items = resp.json()
        if not isinstance(items, list):
            continue
        for raw in items:
            ad = _normalize(raw, kw)
            if ad:
                ads.append(ad)
        print(f"Rakip reklam: '{kw}' -> {len(items)} sonuç")

    # ayni reklami tekrar sayma, en uzun yayinda kalanlari one al
    uniq = {}
    for ad in ads:
        key = ad["library_id"] or (ad["page"], ad["text"][:80])
        uniq.setdefault(key, ad)
    return sorted(uniq.values(), key=lambda a: a["days_running"] or 0, reverse=True)


# ---------------------------------------------------------------------------
# Gemini analizi
# ---------------------------------------------------------------------------
BRIEF_SCHEMA_HINT = """
Sadece şu JSON'u döndür (başka metin yok):
{
  "ozet": "rakiplerin reklamlarında ne gördün, 2-3 cümle, Türkçe",
  "kazanan_kaliplar": ["en uzun yayında kalan reklamların ortak özellikleri, Türkçe, 3-5 madde"],
  "rakiplerin_zayif_yonleri": ["rakiplerin yapmadığı / kötü yaptığı şeyler, 2-3 madde"],
  "bizim_acimiz": "bu videoda rakiplerden nasıl ayrışacağız, 1 cümle",
  "kanca_metni": "videonun ilk 2 saniyesinde ekranda yazacak Türkçe kanca, EN FAZLA 6 kelime",
  "urun_satiri": "ortada çıkacak kısa ürün satırı, Türkçe, EN FAZLA 7 kelime",
  "cta": "kapanış çağrısı, Türkçe, EN FAZLA 4 kelime",
  "paylasim_metni": "Instagram açıklaması, Türkçe, 2-3 kısa satır + 4-5 hashtag",
  "sahneler": [
    {"gorsel_prompt": "ENGLISH prompt for a photoreal 9:16 lifestyle still that shows the exact product", "hareket_prompt": "ENGLISH prompt describing calm camera + subject motion for an 8 second clip"}
  ]
}
"""


def _gemini_client():
    from google import genai

    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY tanımlı değil")
    return genai.Client(api_key=config.GEMINI_API_KEY)


def _extract_json(text: str) -> dict:
    text = (text or "").strip()
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Gemini yanıtında JSON bulunamadı")
    return json.loads(text[start : end + 1])


def _product_context(product) -> str:
    return (
        f"Marka: Loftik Ayakkabı (loftikayakkabi.com)\n"
        f"Ürün: {product.title}\nFiyat: {product.price_text or 'bilinmiyor'}\n"
        f"Kategori: {product.category_slug}\n"
        f"Tarih: {datetime.now().strftime('%d.%m.%Y')} (mevsimi dikkate al)\n"
    )


def _task_text(product, n_scenes: int) -> str:
    return (
        "Sen bir performans reklamcısısın. Türkiye'de ayakkabı satan küçük bir e-ticaret "
        "markası için Instagram Reels / Meta reklam videosu planlıyorsun.\n\n"
        + _product_context(product)
        + f"\nTam olarak {n_scenes} sahne üret. {SCENE_RULES}\n"
        "Her gorsel_prompt ürünü referans fotoğraftaki haliyle birebir tarif etsin "
        "(renk, taban, model) ve kişinin yüzü kadrajda olmasın ya da çok küçük olsun. "
        "Rakiplerde gördüğün kazanan kalıpları kullan ama kopyalama; rakip marka adı, "
        "logo, yanıltıcı indirim veya sahte müşteri yorumu kullanma.\n"
        + BRIEF_SCHEMA_HINT
    )


def analyze_with_ads(product, ads: list[dict], n_scenes: int) -> dict:
    from google.genai import types

    client = _gemini_client()
    top = ads[:25]
    ads_text = "\n".join(
        f"- [{a['page'] or '?'}] {a['days_running'] if a['days_running'] is not None else '?'} gündür yayında, "
        f"{a['format']}, CTA: {a['cta'] or '-'} | {a['text'][:300]!r}"
        for a in top
    )
    parts = [
        _task_text(product, n_scenes)
        + "\n\nTürkiye'de şu an yayında olan rakip reklamlar (en uzun yayında olan en üstte):\n"
        + ads_text
    ]
    # En uzun yayinda kalan 4 reklamin onizleme gorselini de goster
    for ad in top[:4]:
        url = ad.get("preview_image")
        if not url:
            continue
        try:
            img = requests.get(url, timeout=20)
            if img.ok and img.headers.get("content-type", "").startswith("image/"):
                parts.append(types.Part.from_bytes(data=img.content, mime_type=img.headers["content-type"]))
        except requests.RequestException:
            continue

    resp = client.models.generate_content(
        model=config.GEMINI_TEXT_MODEL,
        contents=parts,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    return _extract_json(resp.text)


def analyze_with_search(product, keywords: list[str], n_scenes: int) -> dict:
    """APIFY yoksa: Google aramasiyla rakip reklam trendlerini arastir."""
    from google.genai import types

    client = _gemini_client()
    resp = client.models.generate_content(
        model=config.GEMINI_TEXT_MODEL,
        contents=_task_text(product, n_scenes)
        + "\n\nÖnce Google'da şu konularda Türkiye'deki güncel ayakkabı reklamlarını ve "
        f"Instagram içerik trendlerini araştır: {', '.join(keywords)}. Rakip markaların "
        "(ör. büyük ayakkabı zincirleri ve Instagram butikleri) reklamlarında öne çıkan "
        "kancaları ve formatları çıkar.",
        config=types.GenerateContentConfig(tools=[types.Tool(google_search=types.GoogleSearch())]),
    )
    return _extract_json(resp.text)


def default_brief(product, n_scenes: int) -> dict:
    scene = {
        "gorsel_prompt": (
            "Photoreal vertical 9:16 lifestyle photo: a person wearing EXACTLY the shoes from the "
            "reference image walking on an autumn city street, low camera at knee height, shoes "
            "large and sharp in the lower third, warm natural light, face not visible."
        ),
        "hareket_prompt": (
            "The person keeps walking calmly toward the camera with a steady confident pace, "
            "camera slowly follows at knee height, natural realistic motion."
        ),
    }
    return {
        "ozet": "Rakip analizi yapılamadı, varsayılan plan kullanıldı.",
        "kazanan_kaliplar": [],
        "rakiplerin_zayif_yonleri": [],
        "bizim_acimiz": "",
        "kanca_metni": "Bu sezonun favorisi",
        "urun_satiri": product.title.split(" - ")[-1][:40],
        "cta": "Şimdi incele",
        "paylasim_metni": "",
        "sahneler": [scene] * n_scenes,
    }


def _clean_brief(brief: dict, product, n_scenes: int) -> dict:
    fallback = default_brief(product, n_scenes)
    for key, value in fallback.items():
        if not brief.get(key):
            brief[key] = value
    scenes = [s for s in brief.get("sahneler", []) if s.get("gorsel_prompt") and s.get("hareket_prompt")]
    while len(scenes) < n_scenes:
        scenes.append(fallback["sahneler"][0])
    brief["sahneler"] = scenes[:n_scenes]
    # ekrana sigsin diye kelime sinirlari
    brief["kanca_metni"] = " ".join(str(brief["kanca_metni"]).split()[:6])
    brief["urun_satiri"] = " ".join(str(brief["urun_satiri"]).split()[:7])
    brief["cta"] = " ".join(str(brief["cta"]).split()[:4])
    return brief


def build_brief(product, is_boot: bool = False, n_scenes: int | None = None) -> dict:
    """Rakip analizini yapar, raporu kaydeder ve video brief'ini dondurur."""
    n_scenes = n_scenes or config.AD_SCENES
    keywords = keywords_for(product.title, product.category_slug, is_boot)
    report = {
        "tarih": datetime.now(timezone.utc).isoformat(),
        "urun": product.title,
        "urun_url": product.url,
        "anahtar_kelimeler": keywords,
        "kaynak": None,
        "reklam_sayisi": 0,
        "en_uzun_yayindaki_reklamlar": [],
    }
    brief = None
    ads: list[dict] = []
    try:
        ads = fetch_competitor_ads(keywords)
        report["reklam_sayisi"] = len(ads)
        report["en_uzun_yayindaki_reklamlar"] = ads[:10]
        if ads:
            brief = analyze_with_ads(product, ads, n_scenes)
            report["kaynak"] = "meta_ad_library"
    except Exception as exc:  # noqa: BLE001
        print(f"UYARI: Ad Library taraması yapılamadı ({exc}).")

    if brief is None:
        try:
            brief = analyze_with_search(product, keywords, n_scenes)
            report["kaynak"] = "google_arama"
        except Exception as exc:  # noqa: BLE001
            print(f"UYARI: Google aramalı analiz de başarısız ({exc}), varsayılan plan kullanılıyor.")
            report["kaynak"] = "varsayilan"

    brief = _clean_brief(brief or {}, product, n_scenes)
    report["brief"] = brief

    os.makedirs(config.COMPETITOR_REPORT_DIR, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", product.url.rsplit("/", 1)[-1].lower())[:60]
    path = os.path.join(
        config.COMPETITOR_REPORT_DIR, f"{datetime.now().strftime('%Y-%m-%d_%H%M')}_{slug}.json"
    )
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    brief["_rapor_dosyasi"] = path
    brief["_kaynak"] = report["kaynak"]
    brief["_reklam_sayisi"] = report["reklam_sayisi"]
    brief["_en_uzun"] = ads[:3]
    return brief


def telegram_summary(brief: dict) -> str:
    kaynak = {
        "meta_ad_library": f"Meta Reklam Kütüphanesi ({brief.get('_reklam_sayisi', 0)} rakip reklam)",
        "google_arama": "Google araması (Apify tanımlı değil ya da tarama başarısız)",
        "varsayilan": "YAPILAMADI -- varsayılan plan",
    }.get(brief.get("_kaynak"), "?")
    lines = ["📊 RAKİP REKLAM ANALİZİ", f"Kaynak: {kaynak}", "", brief.get("ozet", "")]
    if brief.get("kazanan_kaliplar"):
        lines += ["", "Kazanan kalıplar:"] + [f"• {k}" for k in brief["kazanan_kaliplar"][:5]]
    if brief.get("rakiplerin_zayif_yonleri"):
        lines += ["", "Rakiplerin zayıf yönü:"] + [f"• {k}" for k in brief["rakiplerin_zayif_yonleri"][:3]]
    longest = brief.get("_en_uzun") or []
    if longest:
        lines += ["", "En uzun yayında olanlar:"]
        for ad in longest:
            lines.append(f"• {ad.get('page') or '?'} -- {ad.get('days_running') or '?'} gün, {ad.get('format')}")
    if brief.get("bizim_acimiz"):
        lines += ["", f"🎯 Bizim açımız: {brief['bizim_acimiz']}"]
    return "\n".join(lines)[:4000]
