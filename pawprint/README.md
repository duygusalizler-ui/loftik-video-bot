# PawPrint Globe — Reel botu

Loftik'ten bağımsız çalışır. Loftik dosyalarına dokunmaz.

**Ne yapar:** Pexels'ten duygusal stok sahneleri ücretsiz olarak çeker (yaşlı köpek, sarılma, pati), sonuna bizim ürün sahnemizi ekler (pati kile basılıyor → iz → küre kapanıyor). Ortaya ~15–18 sn'lik dikey bir Reel çıkar. Videoyu, İngilizce açıklamayı ve Türkçe çevirisini Telegram'a gönderir. **Instagram'a kendisi paylaşmaz.** Paylaşım her zaman onaydan sonra elle yapılır.

## Kurulum (bir kerelik)
Settings → Secrets and variables → Actions → **New repository secret**
| Secret | Zorunlu mu | Açıklama |
|---|---|---|
| `PEXELS_API_KEY` | evet | pexels.com/api adresinden alınan ücretsiz anahtar |
| `PAWPRINT_TELEGRAM_BOT_TOKEN` | hayır | PawPrint için ayrı bir bot. Boş bırakılırsa Loftik botu kullanılır |

`GEMINI_API_KEY`, `TELEGRAM_BOT_TOKEN` ve `TELEGRAM_CHAT_ID` Loftik'ten zaten tanımlı.

## Çalıştırma
Actions → **PawPrint Globe Reel** → Run workflow (adet, tema, yazı seçilebilir).
Otomatik çalışma saatleri: her gün TR 10:20 ve 18:20.

## Dosyalar
- `themes.json`: temalar (Pexels aramaları, kanca cümlesi EN/TR, hangi ürün sahnesinin kullanılacağı). Yeni tema eklemek için buraya bir blok eklemek yeterli.
- `assets/product/`: ürün sahneleri. `full` (15 sn), `press_reveal` (10,6 sn), `globe` (5 sn).
- `data/used.json`: kullanılmış stok klipler (aynı klip iki kez kullanılmaz).
