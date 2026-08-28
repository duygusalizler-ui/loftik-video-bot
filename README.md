# Loftik Video Bot

`loftikayakkabi.com` sitesindeki ürünleri otomatik tarar, Gemini'nin video
modeli (Veo) ile dikey (9:16) ürün videosu üretir, Instagram hikayesine
uygun bir görsel oluşturur, ürün adı + fiyat + 3-5 hashtag içeren bir
açıklama yazar ve hepsini Telegram'a gönderir. GitHub Actions ile günde
birkaç defa otomatik çalışır ve hangi ürünün paylaşıldığını kaydederek
aynı ürünü tekrar seçmez.

## Akış

1. Kategori sayfalarını tarar (**BOT kategorisi otomatik hariç**)
2. Daha önce paylaşılmamış rastgele bir ürün seçer
3. Ürünün fotoğrafını indirir
4. Gemini (Veo) ile referans fotoğraftaki ürünü kullanarak dikey ürün
   videosu üretir (taş kaide üzerinde, gün batımı ışığı — yüklediğiniz
   örnek videoya benzer stil)
5. Instagram hikayesine uygun, marka şablonlu bir görsel üretir
6. Ürün adı + fiyat + link + hashtag içeren açıklama yazar
7. Video + hikaye görselini Telegram kanalına gönderir
8. `data/posted.json` dosyasını günceller (tekrar seçilmesin diye)

## Kurulum

### 1. GitHub'a yükle

```bash
cd loftik-video-bot
git init
git add .
git commit -m "ilk kurulum"
git branch -M main
git remote add origin <YENİ_REPO_URL>
git push -u origin main
```

### 2. Secrets ekle

Repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret adı | Nereden alınır |
|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com/apikey |
| `TELEGRAM_BOT_TOKEN` | Telegram'da @BotFather → `/newbot` |
| `TELEGRAM_CHAT_ID` | Botu kanala ekle, bir mesaj at, sonra `https://api.telegram.org/bot<TOKEN>/getUpdates` adresine bak, `"chat":{"id": ...}` değerini al |

### 3. Workflow izinlerini aç

Repo → **Settings → Actions → General → Workflow permissions** →
**"Read and write permissions"** seç. (posted.json'u otomatik commit
edebilmesi için gerekli.)

### 4. Zamanlama (ÖNEMLİ -- GitHub'ın kendi cron'u yerine dış servis)

GitHub Actions'ın kendi `schedule:` tetikleyicisi bu repoda güvenilir çalışmadı
(hiç ateşlenmedi). Bunun yerine **cron-job.org** (ücretsiz) gibi dış bir
servisten, `workflow_dispatch` endpoint'ine düzenli POST isteği atarak
tetikliyoruz.

**Kurulum:**

1. https://cron-job.org adresinde ücretsiz hesap aç
2. **Create cronjob** → şu bilgileri gir:
   - **URL**: `https://api.github.com/repos/duygusalizler-ui/loftik-video-bot/actions/workflows/auto_post.yml/dispatches`
   - **Request method**: `POST`
   - **Schedule**: Custom → `10 6,8,11,13,16 * * *` (bu, TR saatiyle 09:10, 11:10, 14:10, 16:10, 19:10 demek -- günde 5 kez)
   - **Headers** (Advanced/Headers sekmesinde ekle):
     - `Authorization: Bearer <TOKEN>`
     - `Accept: application/vnd.github+json`
     - `Content-Type: application/json`
   - **Request body**: `{"ref":"main"}`
3. `<TOKEN>` için: github.com → Settings → Developer settings → Personal access
   tokens → Fine-grained tokens → yeni token:
   - Resource owner: `duygusalizler-ui`
   - Repository access: Only select repositories → `loftik-video-bot`
   - Permissions: **Contents** (Read and write), **Workflows** (Read and write)
   - **Expiration**: bu token cron-job.org'da uzun süre kalacak, en uzun
     seçeneği (genelde 1 yıl) seç ve takvime bir hatırlatma koy
4. Kaydet, cron-job.org'un "Test run" / "Execute now" butonuyla bir kere
   elle test et -- Actions sekmesinde yeni bir run görmelisin

Bu token GitHub'a değil, cron-job.org'a kayıtlı olacak -- yani onu Claude'a
tekrar yapıştırman gerekmiyor, doğrudan cron-job.org'un header alanına
kendin gireceksin.

### 5. İlk testi çalıştır

Actions sekmesi → **"Loftik Otomatik Ürün Videosu"** → **"Run workflow"**
ile elle tetikleyip loglara bakabilirsin.

## Yerel test

```bash
pip install -r requirements.txt

# Sadece scraper'ı dener, siteyi kontrol eder (API anahtarı gerekmez)
python -m src.scraper

# Tüm akışı yerelde dener
export GEMINI_API_KEY=...
export TELEGRAM_BOT_TOKEN=...
export TELEGRAM_CHAT_ID=...
python -m src.main
```

## Bilinmesi gerekenler

- **Maliyet**: Gemini video üretimi (Veo) ücretlidir. Google AI
  Studio/Cloud faturanı takip et; günde 4-5 video x aylık maliyeti
  önceden hesapla.
- **BOT kategorisi**: `src/config.py` içindeki `EXCLUDED_CATEGORY_SLUGS`
  ile hariç tutuluyor. Kış gelince tekrar dahil etmek istersen oradan
  `"bot"` değerini kaldırman yeterli.
- **Site yapısı değişirse**: Scraper, sitenin şu anki (Ağustos 2026)
  HTML yapısına göre yazıldı. Site teması değişirse `src/scraper.py`
  içindeki seçicileri güncellemek gerekebilir — `python -m src.scraper`
  ile hızlıca test edebilirsin.
- **"520 Server Error" hatası**: Site bir bot koruması (WAF/Cloudflare vb.)
  arkasında olduğu için scraper `curl_cffi` ile tarayıcı TLS parmak izini
  taklit ediyor + otomatik yeniden deniyor. Bu düzeltmeden sonra da hata
  **sürekli** tekrarlarsa, muhtemel sebep sitenin GitHub Actions'ın
  sunucu IP aralığını toptan engellemesidir — bu durumda tek çözüm bir
  proxy servisi (ör. residential proxy) kullanmak ya da GitHub Actions
  yerine kendi sunucunda (self-hosted runner) çalıştırmaktır. Ara sıra
  (her çalışmada değil) 520 alman normal, otomatik yeniden deneme onu
  zaten çözer.
- **Instagram**: Şimdilik video ve hikaye görseli Telegram'a düşüyor,
  oradan Instagram'a elle paylaşabilirsin (günde 2 defa istediğin gibi
  planlayabilirsin). Instagram Graph API ile tam otomatik paylaşım için
  Meta Business hesabı + app review süreci gerekiyor — hazır olduğunda
  bunu da ekleyebiliriz (v2).
- **Hikaye linki**: Instagram'ın "link sticker"ını API'den otomatik
  eklemek hesap tipine göre kısıtlı olabildiği için, link bilgisini
  görselin üzerine yazıyoruz; hikayeyi paylaşırken link sticker'ı elle
  ekleyebilirsin.
- **Tekrar paylaşmama mantığı**: `data/posted.json`, her çalışmadan sonra
  GitHub Actions tarafından otomatik commit'lenir. Bu dosyayı elle silme.
