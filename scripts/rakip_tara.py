"""Meta Reklam Kütüphanesi (TR) taraması: bizim ölçeğimizdeki ayakkabı satıcılarının reklamları.
Büyük zincirler elenir. Çıktı: cikti/rakip/rakip_reklamlar.json + rapor.md"""
import json, os, sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src import competitor_ads, config  # noqa: E402

config.COMPETITOR_ADS_PER_KEYWORD = 40
KELIMELER = ["erkek bot", "chelsea bot", "erkek spor ayakkabı", "kapıda ödeme ayakkabı",
             "chekich", "deri bot erkek", "kışlık bot", "ortopedik ayakkabı erkek"]
BUYUK = ["flo", "hotiç", "hotic", "derimod", "kemal tanca", "ayakkabı dünyası", "ayakkabi dunyasi", "trendyol",
         "hepsiburada", "nike", "adidas", "skechers", "puma", "lumberjack", "polaris", "kinetix", "in street",
         "instreet", "sneaks up", "superstep", "boyner", "lc waikiki", "defacto", "koton", "zara", "mavi",
         "tergan", "greyder", "dockers", "u.s. polo", "us polo", "converse", "vans", "new balance", "occasion",
         "marjin", "pierre cardin", "amazon", "n11", "ciceksepeti", "çiçeksepeti", "pttavm", "morhipo"]

ads = competitor_ads.fetch_competitor_ads(KELIMELER)
kucuk = [a for a in ads if a.get("page") and not any(b in a["page"].lower() for b in BUYUK)]
os.makedirs("cikti/rakip", exist_ok=True)
json.dump({"tum": ads, "kucuk": kucuk}, open("cikti/rakip/rakip_reklamlar.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
sayfa = Counter(a["page"] for a in kucuk)
satir = [f"# Rakip reklam taraması\nToplam {len(ads)} reklam, küçük satıcı {len(kucuk)} reklam, {len(sayfa)} sayfa\n",
         "## En çok reklam veren küçük sayfalar"]
satir += [f"- {p}: {n} reklam" for p, n in sayfa.most_common(25)]
satir.append("\n## En uzun süredir yayında olan küçük satıcı reklamları (kazananlar)")
for a in kucuk[:40]:
    satir.append(f"\n### {a['page']} — {a['days_running']} gün — {a['format']} — [{a['keyword']}]\n"
                 f"https://www.facebook.com/ads/library/?id={a['library_id']}\n"
                 f"CTA: {a.get('cta')} | Başlık: {a.get('title')}\n> " + (a['text'] or '').replace("\n", " ")[:500])
open("cikti/rakip/rapor.md", "w", encoding="utf-8").write("\n".join(satir))
print("\n".join(satir[:30]))
