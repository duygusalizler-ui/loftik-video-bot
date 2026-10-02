# storyads — Hikâyeli reklam motoru

Bir ürün linkinden **reklam gibi durmayan**, paylaşılan kısa hikâye videosu üretir.
Markadan bağımsızdır: Loftik ilk marka, yeni müşteri = `brands/` altına yeni bir JSON dosyası.

## Ne üretir?
- **video.mp4**: 5 sahne, ~20-28 sn, dikey 9:16
  - Animasyon karakterler, gerçekçi arka plan, **gerçek gibi duran ürün**
  - Akış: **kanca → sorun → öneri → ürün (farklı bakış açısı) → sonuç (mutluluk)**
  - Seslendirme yok. Sahnelerin kendi ses efektleri var, altında kısık müzik.
  - Yumuşak geçişler. Hikâyeyi sessiz izleyen de anlasın diye kısa ekran yazıları var.
  - Sonda fiyat ya da ürün kartı **yok**; video vurucu bir cümleyle biter.
- **aciklama.txt**: hikâyenin devamı gibi bir açıklama, paylaşım çağrısı, bio/site yönlendirmesi, hashtag'ler ve müzik kredisi
- **sabit_yorum.txt**: markanın kendi yorumu (ürün adı + nereden alınır)
- **plan.json** (senaryo), **kalite.json** (kalite kontrol puanları), **kareler.jpg** (hızlı önizleme)

## Nasıl çalışır?
1. `product.py` ürün sayfasını okur: JSON-LD/OpenGraph üzerinden ad, fiyat ve gerçek fotoğraflar alınır. Her e-ticaret sitesinde çalışır.
2. `planner.py` Gemini ile senaryo yazar. Format ve karakter her seferinde farklı seçilir; son kullanılanlar tekrar edilmez. Formatlar `formats.py` içinde: rövanş, saat damgası, sırları ne?, POV, beklenti/gerçek, küçük kahraman, sayaç.
3. `pipeline.py` her sahne için şunları yapar:
   - Gemini görsel üretir.
   - Kalite kontrolü yapılır: ürün aynı mı, fazla uzuv/logo var mı, karakter tutarlı mı. Geçemeyen görsel yeniden üretilir.
   - Veo ile ses efektli klip üretilir.
   - Klip **kare kare** kontrol edilir (~0,6 sn arayla): fazladan ayakkabı, karışan yüzler ya da bulanıkta kaybolan yüz gibi hatalı anlar bulunur. Kurguda yalnızca klibin temiz aralığı kullanılır.
4. `editor.py` kurguyu yapar: xfade geçişleri, ekran yazıları, müzik ve ses seviyesi dengesi. Sahne başına klip aralığı (`bas`/`son`), final yazısının konumu ve zamanlaması (`final_y`/`final_bas`) ayarlanabilir.
5. `music.py` hikâyenin moduna göre `music/` klasöründen parça seçer. Kredi gerekiyorsa açıklamaya otomatik eklenir.

## Çalıştırma
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=...
python -m storyads --marka loftik --urun https://www.loftikayakkabi.com/urun/mn223-cst-alaska-erkek-bot-taba
python -m storyads --marka loftik --urun URL --format rovans --karakter ayı   # elle seçim
python -m storyads --formatlar
```
GitHub'da: **Actions → "Hikâye videosu" → Run workflow**. Ürün linkini girince sonuç Telegram'a gelir.

## Yeni müşteri eklemek
1. `brands/_ornek.json` dosyasını `brands/<kod>.json` olarak kopyala.
2. Sektör, hedef kitle, ses tonu, bio cümlesi, yasaklar ve ürün notlarını doldur.
3. `python -m storyads --marka <kod> --urun <link>` ile çalıştır.

## Ayarlar (ortam değişkenleri)
| Değişken | Varsayılan | Anlamı |
|---|---|---|
| `STORYADS_SCENES` | 5 | sahne sayısı |
| `STORYADS_CLIP_SECONDS` | 6 | klip süresi |
| `STORYADS_QA_MIN` | 7 | kalite eşiği (10 üzerinden) |
| `STORYADS_MUSIC_VOLUME` | 0.22 | müzik seviyesi (ses efektleri 1.0) |
| `STORYADS_VIDEO_MODEL` | veo-3.1-fast-generate-preview | video modeli |

## SaaS'a dönüşürken
- `brands/*.json` → müşteri paneli (form)
- `cikti/` → müşterinin video kütüphanesi
- `pipeline.run()` tek giriş noktası; bir kuyruk/worker arkasına konur.
- `genai.py` sağlayıcı katmanı; Kling/Higgsfield gibi başka sağlayıcılar buraya eklenir.
