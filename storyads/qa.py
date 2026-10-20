"""Otomatik kalite kontrolu (Gemini vision): hatali kare/klip yayina gitmesin."""
from __future__ import annotations

from . import genai, settings

QA_PROMPT = """Sen kısa video reklamları için katı bir kalite kontrolcüsün.
İlk {n_ref} görsel: ürünün GERÇEK fotoğrafı (referans){karakter_notu}.
Sonraki görsel(ler): yapay zekâyla üretilmiş sahne kare(leri).
Beklenen üslup: karakterler 3D animasyon, arka plan gerçekçi fotoğraf, ürün %100 gerçek ürün fotoğrafı gibi.
Ürün sahnede görünmeli mi: {urun_gorunur}

Kontrol et:
1. Ürün görünüyorsa referansla aynı mı (şekil, renk, taban/detaylar)? Animasyon/plastik mi duruyor (kötü)?
2. Anatomi hatası: fazla ayak/el/bacak, havada duran fazladan ürün, eriyen şekiller.
3. Uydurma logo, marka, NET okunur yazı, sayı, sayaç, konuşma balonu var mı (olmamalı)? Uzakta bulanık,
   okunmayan dükkân tabelası hata DEĞİLDİR.
4. Karakter önceki sahneyle tutarlı mı (verildiyse)?
5. Görüntü bozulması, garip yüz, mantıksız arka plan.
6. (Ürün görünmesi gerekiyorsa) Ürün göze çarpıyor mu ve ÇEKİCİ mi? Kadrajda net, iyi ışıklı, sahnenin dikkat
   çeken öğesi mi; izleyici bu ürünü beğenir mi? Ürün küçük/karanlık/bulanık/kirli ise puan en fazla 6.

Sadece JSON: {{"urun_uyumu": 0-10, "urun_cekiciligi": 0-10, "urun_plastik_mi": true/false, "anatomi": 0-10, "logo_yazi_yok": 0-10, "tutarlilik": 0-10, "hatalar": ["kısa Türkçe"], "puan": 0-10}}
"urun_plastik_mi": ürün görünüyor ama gerçek ürün fotoğrafı yerine animasyon/3D/plastik duruyorsa true
(true ise puan en fazla 4: ürün ASLA animasyon görünmez).
Ürün görünmesi gerekmiyorsa ürün yokluğundan puan KIRMA.
"puan" = en kritik sorunun belirlediği genel puan. Fazla uzuv / fazladan ürün / logo varsa puan en fazla 4."""


def score(product_refs: list[str], candidates: list[str], urun_gorunur: bool = True,
          character_ref: str | None = None) -> dict:
    refs = list(product_refs[:2]) + ([character_ref] if character_ref else [])
    prompt = QA_PROMPT.format(
        n_ref=len(product_refs[:2]), urun_gorunur="evet" if urun_gorunur else "hayır (görünmese de olur)",
        karakter_notu=", son referans: önceki sahne (karakter tutarlılığı için)" if character_ref else "",
    )
    try:
        r = genai.text_json(prompt, refs + candidates)
        r["puan"] = int(r.get("puan", 0))
    except genai.QuotaError:
        raise
    except Exception as exc:  # noqa: BLE001
        r = {"puan": 0, "hatalar": [f"kalite kontrolü çalışmadı: {exc}"]}
    r["gecti"] = r["puan"] >= settings.QA_MIN
    return r


CLIP_PROMPT = """Sen kısa video reklamları için katı bir kalite kontrolcüsün.
İlk {n_ref} görsel: ürünün GERÇEK fotoğrafı (referans). Sonraki görsel: klibin başlangıç karesi (karakter referansı).
Sonraki {n} görsel: aynı video klibinden sırayla alınmış kareler,
zamanları (sn): {zamanlar}.
Beklenen üslup: karakterler 3D animasyon, arka plan gerçekçi fotoğraf, ürün %100 gerçek ürün gibi.
Bu sahnede ürün görünmeli mi: {urun_gorunur}. Görünmemesi gerekiyorsa karakterin eski/başka ayakkabı giymesi
DOĞRUDUR, bundan puan kırma; sadece başlangıç karesiyle tutarlılığa ve bozulmalara bak.

Her kareyi tek tek kontrol et: fazla ayak/kol/ayakkabı (ör. karakter ayakkabı giymişken yerde de bir çift durması),
karakterlerin birbirine karışması/eriyen yüz, bulanıklıkta kaybolan yüz, ürünün animasyona dönmesi veya değişmesi,
karakterin yüzünün/tipinin başlangıç karesine göre değişmesi, nesnenin aniden belirmesi/kaybolması/şekil değiştirmesi,
NET okunur anlamsız yazı, uydurma logo (uzakta bulanık tabela hata değil).
Ürün görünmesi gerekiyorsa: ürün herhangi bir karede animasyon/3D/plastik görünüyorsa o kare hatalıdır.
Kısa hareket bulanıklığı tek başına hata değildir.

Ayrıca son karelerde ana karakterin yüzü ekranın neresinde: "ust", "orta" veya "alt" (yüz görünmüyorsa "yok").
Sadece JSON: {{"hatali_kareler": [{{"sn": 0.0, "sorun": "kısa Türkçe"}}], "urun_uyumu": 0-10, "puan": 0-10, "hatalar": ["kısa Türkçe"], "son_yuz_konumu": "ust|orta|alt|yok"}}
"puan" = klibin TEMİZ kısmı reklamda kullanılabilir mi (hatalı anlar kesilecek)."""


def clean_range(times: list[float], bad: list[float], total: float, min_len: float = 2.4) -> tuple[float, float] | None:
    """Hatali karelerin etrafini kesip en uzun temiz araligi dondurur."""
    step = (times[1] - times[0]) if len(times) > 1 else total
    cuts = sorted(bad)
    edges = [0.15] + [x for b in cuts for x in (b - step * 0.75, b + step * 0.75)] + [total]
    best = None
    for a, b in zip(edges[::2], edges[1::2]):
        a, b = max(a, 0.15), min(b, total)
        if b - a >= min_len and (best is None or b - a > best[1] - best[0]):
            best = (round(a, 2), round(b, 2))
    return best


def score_clip(product_refs: list[str], frames: list[str], times: list[float], total: float,
               start_image: str | None = None, urun_gorunur: bool = True) -> dict:
    prompt = CLIP_PROMPT.format(n_ref=len(product_refs[:2]), n=len(frames), zamanlar=", ".join(f"{t:.1f}" for t in times),
                                urun_gorunur="evet" if urun_gorunur else "HAYIR")
    try:
        r = genai.text_json(prompt, list(product_refs[:2]) + ([start_image] if start_image else []) + frames)
        r["puan"] = int(r.get("puan", 0))
    except genai.QuotaError:
        raise
    except Exception as exc:  # noqa: BLE001
        return {"puan": 0, "gecti": False, "hatalar": [f"kalite kontrolü çalışmadı: {exc}"]}
    bad = [float(h.get("sn", 0)) for h in r.get("hatali_kareler") or [] if isinstance(h, dict)]
    r["aralik"] = clean_range(times, bad, total)
    r["gecti"] = r["puan"] >= settings.QA_MIN and r["aralik"] is not None
    return r
