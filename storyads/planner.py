"""Gemini ile hikaye plani (senaryo + sahne promptlari + aciklama metni)."""
from __future__ import annotations

import json
import os
import random

from . import genai, settings
from .brand import Brand
from .formats import CHARACTERS, FORMATS
from .product import Product

PLAN_PROMPT = """Sen Instagram Reels / TikTok için organik görünen, paylaşılan kısa hikâye videoları yazan bir yaratıcı yönetmensin.
Amaç: izleyici videoyu eğlenerek izlesin ve bitirdiğinde ÜRÜNÜ FARK ETMİŞ VE BEĞENMİŞ olsun.
Marka: {marka} ({sektor}). Hedef kitle: {kitle}. Ses tonu: {ton}.
Ürün: {urun} | Fiyat: {fiyat} | Açıklama: {aciklama}
Ürüne özel not: {urun_notu}
Ekte ürünün GERÇEK fotoğrafları var.

FORMAT: "{format_ad}" — {format_fikir}
ANA KARAKTER: {karakter} (3D animasyon film karakteri gibi, insan gibi giyinmiş ve davranan). Gerekirse 1-2 yan karakter (yine hayvan, farklı tür) ekleyebilirsin.

KURALLAR (hepsi zorunlu):
1. Tam {n} sahne, sırasıyla rolleri: kanca (ilk 2 saniyede dikkat çeken komik/çarpıcı an) -> sorun -> öneri -> ürün -> sonuç (mutluluk, gerekirse küçük komik ters köşe).
   HİKÂYE TUTARLI OLMALI: kanca ve sorun sahnelerinde karakter ürünü KULLANMIYOR (eski/kötü/uygunsuz bir şeyle
   başı dertte); ürün ilk kez "oneri" sahnesinde ortaya çıkar; sonrasında karakter ürünü kullanır.
   Kanca örnekleri (bu kalitede yaz, kopyalama): "Kışın en kötü 3 saniyesi", "17:45 — ayaklarım istifa etti",
   "POV: yağmur başladı ve sen beyaz ayakkabıdasın". Final örnekleri: "Kış: 0 — Ayı: 1", "17:45 — enerji hâlâ %100".
2. Video SESSİZ izleyen birine bile hikâyeyi NET anlatmalı: her sahnenin "ekran_yazisi" en fazla 7 kelime, çarpıcı, günlük Türkçe. İlk sahnenin yazısı "kanca" alanıdır.
3. Seslendirme ve konuşma YOK. Her sahneye gerçekçi ses efekti tarifi yaz (adım, su sıçraması, kapı, ofis uğultusu, komik 'ding' vb.). Müzik ayrıca eklenecek, klipte müzik olmayacak.
4. Ürün tanıtımı klasik olmasın: "ürün" sahnesi farklı bir bakış açısı kullansın (yerden çekim, birinci şahıs, yan yana dizilim, rövanş anı...) ama hikâyeye bağlı olsun ve sonuca bağlansın.
5. Videoda marka adı, fiyat, site, logo, ürün kartı YOK. Reklam gibi değil, eğlenceli bir hikâye gibi dursun. Son sahne "final_yazi" ile biter (vurucu, akılda kalan, paylaşılabilir).
6. Görsel üslup: karakterler animasyon, ARKA PLAN TAMAMEN GERÇEKÇİ fotoğraf (gerçek Türkiye mekânı), ÜRÜN %100 GERÇEK ürün fotoğrafı gibi (animasyon değil), ekteki fotoğraftaki ürünün birebir aynısı.
7. Hareketler gerçek zamanlı hızda, AĞIR ÇEKİM YOK. Her sahne tek kesintisiz çekim (~5-6 sn).
8. Görsel/hareket/ses promptları İNGİLİZCE, ekran yazıları ve açıklama TÜRKÇE.
9. Açıklama (caption) — YORUM TAKTİĞİ (kesin kural): izleyicilerin çoğu markayı tanımayan yabancılardır.
   1. satır: herkesin 1 saniyede cevaplayabileceği soru (tercihen emoji seçmeli: "Sen hangisisin? 😩 Dünkü X / 😎 Bugünkü X").
   2. satır: satış çağrısı ("Ürünü isteyen <KELİME> yazsın, linki DM'den atalım").
   "sabit_yorum": markanın kendi yorumu olarak "Sıradaki bölümde <karakter> nereye gitsin? 👇" + 3 emojili seçenek
   (izleyici bir sonraki bölümü seçer, seri takibi getirir). Ürün adı ve link DM'de verilir.
   Site adresi: {site} (başka adres UYDURMA).
10. AKICILIK: Video DOĞRUDAN hikâyeyle başlar; başa ürün ön gösterimi/özet çekimi KOYMA (kesin kural).
   İlk sahne hareketli ve çarpıcı olsun, hareketsiz duran karakter yok. Her sahnenin "hareket_prompt"u 2-3 hızlı
   çekimden oluşsun: "Shot 1: ... Shot 2: ... Shot 3: ...", her çekim ~2 sn. Sahneler arası akış kesintisiz.
   ÜRÜN BİLİNÇALTI (kesin kural): Ürün her sahnede göze çarpsın ama "reklam" gibi itilmesin: ürünü taşıyan
   karakter (ya da sahnedeki başka biri) ürünü doğal biçimde kadrajda taşır, kamera ürüne sık sık ama kısa
   (≤1 sn) değer, ürün sahnenin en canlı/aydınlık rengi olur. Kanca ve sorun sahnelerinde bile ürün arka planda
   biri tarafından giyilmiş olarak kısa görünebilir (izleyici fark etmeden aklında kalır).
10b. KOMEDİ + PAYLAŞIM (kesin kural): "sonuc" sahnesinden sonra herkesin yaşadığı, güldüren bir TERS KÖŞE gelir
   ("ters_kose_yazisi", ör. 'Patron: "Madem enerjin var, mesaiye kal."'), video ekranda bir PAYLAŞIM/ETİKET
   çağrısıyla biter ("paylasim_yazisi", ör. "Mesaiye kalan arkadaşına gönder"). Ürün bu sahnede de kadrajdadır.
11. ÜRÜN GERÇEKLİĞİ (KESİN KURAL): Ürün asla animasyon/3D/plastik görünmez. "urun" sahnesi ve ürünün yakın
   göründüğü her çekim KARAKTERSİZ olur: sadece pantolon paçası + ürün, %100 gerçek fotoğraf/telefon çekimi gibi
   ("Real smartphone footage, photorealistic, not CGI"). Karakter bu sahnede ya hiç görünmez ya da uzakta bulanık kalır.
12. HATA ÖNLEME (yapay zekâ videosunda en çok bozulan şeyler, bunlardan kaçın):
   - Bir sahnede en fazla 2 karakter; karakterler birbirinin önünden geçmesin, iç içe girmesin.
   - Zıplama, koşma, dans, hızlı dönüş YOK; sakin ve tek bir hareket (yürür, uzatır, bakar, oturur).
   - Ayakkabı/ürün giyme-çıkarma, el değiştirme YOK; ürün sahnede tek bir yerde dursun (ya ayakta ya elde).
   - Ürün her sahnede aynı sayıda: bir çift ayakkabı = 2 ayakkabı, fazlası yok.
   - Okunabilir yazı, tabela, ekran, logo içeren arka plan YOK. "gorsel_prompt" ve "hareket_prompt" içinde
     sayı, saat, sayaç, yazı, konuşma balonu, arayüz ASLA geçmesin (bunlar sadece ekran yazısında olur).
   - Kutu/paket açma, nesnenin aniden belirmesi/kaybolması YOK; ürün zaten sahnededir.
   - Ürün sadece "oneri", "urun" ve "sonuc" sahnelerinde görünür ("urun_gorunur": true); kanca ve sorun
     sahnelerinde ürün yoktur (karakter eski/kötü ayakkabıyla olabilir).
   - Kadrajın üst %20'si sakin arka plan olsun (gökyüzü/duvar), karakterin başı bunun ALTINDA; en alt %20 de
     yazıya ayrılır. Bunu her "gorsel_prompt"a yaz.
13. Asla: {yasak}

Sadece şu JSON'u döndür:
{{
 "karakter_tarifi": "ana karakterin İngilizce kalıcı görünüm tarifi (tür, kürk rengi, kıyafet) — tüm sahnelerde aynı",
 "yan_karakterler": ["İngilizce kısa tarif"],
 "kanca": "ilk sahnenin ekran yazısı",
 "sahneler": [
   {{"rol": "kanca|sorun|oneri|urun|sonuc",
     "ekran_yazisi": "Türkçe (ilk sahnede boş bırak)",
     "gorsel_prompt": "İngilizce: sahnenin ilk karesi — mekân, kamera açısı, karakter pozu, ürün nerede",
     "hareket_prompt": "İngilizce: 5-6 sn içinde ne olur, kamera hareketi",
     "ses_efekti": "İngilizce: duyulacak sesler",
     "urun_gorunur": true}}
 ],
 "final_yazi": "sonuç sahnesinde çıkacak vurucu cümle",
 "ters_kose_yazisi": "sonuçtan sonra gelen komik ters köşe (kısa)",
 "paylasim_yazisi": "videonun en sonunda ekranda: arkadaşına gönder/etiketle çağrısı (kısa)",
 "aciklama": "Instagram açıklaması",
 "sabit_yorum": "Sıradaki bölüm sorusu + 3 emojili seçenek",
 "dm_kelimesi": "yorumda/DM'de istenecek tek kelime, büyük harf (ör. KIŞ, ENERJİ)",
 "dm_mesaji": "DM'de gönderilecek hazır mesaj: selam + ürün adı + {site} ürün linki + beden/kargo sorusu daveti",
 "hashtagler": ["#...", "(tam 5 adet)"],
 "muzik_modu": "komik|enerjik|neseli|duygusal"
}}"""


def _history() -> dict:
    try:
        with open(settings.HISTORY_FILE, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def remember(brand: Brand, fmt: str, karakter: str) -> None:
    h = _history()
    b = h.setdefault(brand.kod, {"formatlar": [], "karakterler": []})
    b["formatlar"] = (b["formatlar"] + [fmt])[-len(FORMATS) + 1:]
    b["karakterler"] = (b["karakterler"] + [karakter])[-6:]
    os.makedirs(os.path.dirname(settings.HISTORY_FILE) or ".", exist_ok=True)
    with open(settings.HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=1)


def next_product(brand: Brand) -> str:
    """Seri uretim: urun listesinden henuz kullanilmamis ilk urun (liste bitince basa doner)."""
    from .brand import BRANDS_DIR

    path = BRANDS_DIR / f"{brand.kod}_urunler.txt"
    urls = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")]
    if not urls:
        raise SystemExit(f"Ürün listesi boş: {path}")
    used = set(_history().get(brand.kod, {}).get("urunler", []))
    fresh = [u for u in urls if u not in used]
    if not fresh:  # tur tamamlandi, bastan
        h = _history()
        h.setdefault(brand.kod, {})["urunler"] = []
        _save(h)
        fresh = urls
    return fresh[0]


def remember_product(brand: Brand, url: str) -> None:
    h = _history()
    b = h.setdefault(brand.kod, {"formatlar": [], "karakterler": []})
    b["urunler"] = b.get("urunler", []) + [url]
    _save(h)


def _save(h: dict) -> None:
    os.makedirs(os.path.dirname(settings.HISTORY_FILE) or ".", exist_ok=True)
    with open(settings.HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(h, f, ensure_ascii=False, indent=1)


def choose(brand: Brand, fmt: str | None = None, karakter: str | None = None) -> tuple[str, str]:
    """Son kullanilanlari tekrar etmeyen format + karakter."""
    h = _history().get(brand.kod, {})
    if not fmt:
        fresh = [k for k in FORMATS if k not in h.get("formatlar", [])] or list(FORMATS)
        fmt = random.choice(fresh)
    if not karakter:
        pool = brand.karakterler or CHARACTERS
        fresh = [c for c in pool if c not in h.get("karakterler", [])] or pool
        karakter = random.choice(fresh)
    return fmt, karakter


def _urun_notu(brand: Brand, product: Product) -> str:
    t = product.ad.lower()
    return " ".join(v for k, v in brand.urun_notlari.items() if k.lower() in t) or "-"


def make_plan(brand: Brand, product: Product, fmt: str, karakter: str) -> dict:
    f = FORMATS[fmt]
    prompt = PLAN_PROMPT.format(
        marka=brand.ad, sektor=brand.sektor, kitle=brand.hedef_kitle, ton=brand.ses_tonu,
        urun=product.ad, fiyat=product.fiyat or "-", aciklama=product.aciklama or "-",
        urun_notu=_urun_notu(brand, product), format_ad=f["ad"], format_fikir=f["fikir"],
        karakter=karakter, n=settings.SCENES, bio_cta=brand.bio_cta, site=brand.site.replace("https://", "").replace("www.", ""),
        yasak="; ".join(brand.yasak) or "-",
    )
    plan = genai.text_json(prompt, product.gorseller[:2])
    sahneler = plan.get("sahneler") or []
    if len(sahneler) < 3:
        raise RuntimeError(f"Plan eksik geldi: {plan}")
    plan["sahneler"] = sahneler[: settings.SCENES]
    for sc in plan["sahneler"]:
        if sc.get("rol") in ("kanca", "sorun"):
            sc["urun_gorunur"] = False
    plan["format"], plan["karakter"] = fmt, karakter
    # uydurma site adresi olmasin: metindeki her alan adini markanin sitesiyle degistir
    import re
    site = brand.site.replace("https://", "").replace("www.", "").rstrip("/")
    for k in ("aciklama", "sabit_yorum"):
        plan[k] = re.sub(r"\b(?:www\.)?[\w-]+\.(?:com\.tr|com|net|shop|store)\b", site, plan.get(k) or "")
    tags = list(dict.fromkeys((plan.get("hashtagler") or []) + brand.hashtagler))
    plan["hashtagler"] = tags[:5]
    return plan


def caption_text(brand: Brand, plan: dict, music_credit: str | None) -> str:
    parts = [plan.get("aciklama", "").strip(), brand.guven_satiri, " ".join(plan["hashtagler"])]
    if music_credit:
        parts.append(f"Müzik: {music_credit}")
    return "\n\n".join(p for p in parts if p)
