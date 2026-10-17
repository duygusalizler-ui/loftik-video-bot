# Unfrozen History — video hattı

*History, lived from the inside.* Tarihte sıradan insanların zor mevsimleri nasıl atlattığını, o dönemde yaşayan kurgusal ama tarihe sadık bir karakterin ağzından anlatan 10–12 dakikalık videolar.

## Akış

1. **Senaryo + sahne listesi** → `episodes/epXXX/episode.json`, okunabilir hali `SCRIPT.md` → **Kapı 1 onayı** (0 kredi)
2. **Oyuncu kadrosu (referans kartları)** → her karakter + ana mekânlar için 1 kart (1'er kredi); her sahnenin görseli ve klibi bu kartlarla üretilir → karakter/mekân tutarlılığı
3. **Önizleme** (ilk 3 sahne ≈ 60 sn, ~26 kredi) → **Kapı 2 onayı**
4. **Tam üretim** → montaj → YouTube'a *liste dışı* yükleme → **Kapı 3 onayı** → herkese açık

Sahne başına: 1 başlangıç karesi (`gpt_image_2`, medium, 1k, 16:9 = 1 kredi) + 1 klip (`seedance_2_0_mini`, 15 sn, 480p, ortam sesli = 7,5 kredi). Her klip 3 açılı çekim (~5 sn/açı) olarak istenir.
Her sahne ≈ 20 sn anlatım; klip, anlatım süresine göre yavaşlatılır (en fazla 0,65x, ara kare üretimli), 1080p'ye büyütülür (lanczos + unsharp).

## Senaryo kuralları (Operatör Oyun Kitabı)

- Soğuk açılış + fragman: ilk kare somut an, 3–8 sn'de ödül vaadi, sonra mini-ödül ve yolculuk
- Her ~2,5 dk'da bir kırılma (`beat` alanı), büyük ödül sona saklı
- Kısa cümleler, duyusal detay; sahne başına ≈ 20 sn anlatım (en fazla ~22,5 sn)
- Anlatım altında ortam sesi (ASMR katmanı), her şey İngilizce
- Açıklamanın ilk 2 satırı videoya özel (`hook_description`); başlık ≠ kapak
- Tekrar engeli: `data/used_topics.json`

## Bütçe korumaları (`uh/state.py`)

- Video başına en fazla **300**, ay başına en fazla **1.200** kredi
- Bakiye **500**'ün altına inecekse başlamaz (Sunny rezervi)
- Senaryo onayı yoksa hiçbir şey üretilmez; önizleme onayı yoksa sadece önizleme sahneleri
- Her job id gönderildiği anda `data/ledger.json`'a yazılır; biten varlık asla yeniden üretilmez
- Varlık başına en fazla 1 tekrar deneme, sonra durur

## Komutlar

```bash
pip install -r requirements.txt   # + sistemde ffmpeg
python -m uh.cli status ep001
python -m uh.cli doc ep001                        # SCRIPT.md üret
python -m uh.cli approve ep001 script             # kapı 1
python -m uh.cli check ep001 1 image --balance N  # bütçe kontrolü + üretim parametreleri
python -m uh.cli submitted ep001 1 image JOB_ID
python -m uh.cli result ep001 1 image JOB_ID --ok --url URL
python -m uh.cli tts ep001                        # Edge TTS anlatım (ücretsiz)
python -m uh.cli render ep001 --scenes 1-3        # önizleme montajı
python -m uh.cli render ep001 --music music.mp3   # tam montaj (kapı 2 onayı gerekir)
```

## Higgsfield API notu

Higgsfield'ın resmi API'si (cloud.higgsfield.ai) **ayrı ürün, ayrı faturalama**: USD ön ödemeli bakiye kullanır, Ultra abonelik kredilerini **kullanmaz**. Bu yüzden üretim, haftalık bir Claude Code oturumunda Higgsfield MCP ile yapılır; montaj ve yükleme ayrı adımdır. Onay kapıları aynı kalır.

## Sonraki adımlar

- Telegram onay mesajları, YouTube Data API yükleme (liste dışı), GitHub Actions montaj iş akışı
- Otomatik senaryo (Claude Sonnet: taslak → bölümler → kalite kontrol)
- Almanca ses kanalı (`de-DE-ConradNeural`)
