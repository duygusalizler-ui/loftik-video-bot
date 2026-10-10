# Unfrozen History — her bölüm için kontrol listesi

Kaynak: kanal sahibinin verdiği strateji şablonu + Operatör Oyun Kitabı. Her yeni bölüm senaryosu bu 5 adımdan geçmeden Kapı 1'e gelmez.

## 1. Konu — geniş kitle
- Başlık "tarih meraklısı" değil **herkes** için olmalı: *How medieval peasants survived winter without heating* ✔︎ — *Thermal properties of 14th-century wattle-and-daub* ✘
- Hedef: izleyen herkes "bu bana lazım/ilginç" desin.
- Tekrar engeli: `data/used_topics.json`.

## 2. Paketleme üçgeni (üçü birlikte çalışır)
1. **Başlık** → kafada soru işareti açar (cevabı vermez).
2. **Kapak** → başlığı tekrar etmez, tamamlar; en fazla 3–4 kelime (ya da yazısız; A/B test).
3. **İlk 20 saniye** → başlığın sözünü **açıkça** tekrar eder: *"…and I will show you exactly how we survived."*
- Selam, logo animasyonu, "bu videoda…" girişi **yok**.
- **Etiketler cümle halinde** (insanların aradığı arama cümleleri, örn. *how did people survive winter in the middle ages*), tek kelime değil; toplam ≤ 500 karakter, en başta başlığa en yakın cümle, en sonda kanal adı.
- Açıklamanın en sonuna **3 hashtag** (ilk 3'ü başlığın üstünde görünür): `#History #MiddleAges #UnfrozenHistory` gibi — konu + dönem + kanal. 3'ten fazla koyma.
- Yüklemeden önce: aynı konuyu İngilizce YouTube'da ara, üst sıradaki kapakları yan yana koy, bizimkini aralarında test et.

## 3. Metin — çatışma ("ama") yapısı
- Bilgi tek seferde yığılmaz; parçalara bölünür.
- Her bölüm (~2,5 dk) **"ama / but"** ile yeni bir problemle biter → izleyici sonraki bölüme bağlanır.
- Karakter → sorun → çözüme yaklaşma → yeni engel → … → büyük ödül en sonda.
- `episode.json` içinde `beat` alanı bu kırılmaları işaretler.

## 4. Kurgu — kontrollü değişim
- Görüntü düzenli aralıklarla değişir (sahne başına 3 açı, ~5–7 sn), ama rastgele efekt yağmuru yok.
- **Ses görüntüden önemlidir:** her bölümün müziği o bölümün duygusuna göre değişir (`music` planı); müzik anlatım konuşurken alçalır, aralarda yükselir; altında ortam sesi (ASMR) vardır.
- Anlatım sesi sahnenin duygusuna göre yönlendirilir (`voice_mood`: tense / warm / intrigue / festive / relief / outro).

## 5. Zincir — sonraki videoya bağla
- Senaryo yazılırken bir sonraki bölüm de belli olur.
- Final, izleyicinin önüne **yeni bir soru** koyar ve somut sonraki bölümü tanıtır (`next_episode_tease`).
- Bitiş ekranı son 20 sn'deki sakin sahneye konur; o sonraki bölüme bağlanır.

## 6. Niş kuralı: sadece KIŞ — ama "ünlü kışlar" (2026-09-30 analiz)
Viral tarih videolarının ortak noktası: herkesin bildiği bir olay + "sen oradasın" hissi.
Biz nişten çıkmıyoruz; **tarihin ünlü kışlarını**, orada yaşayan sıradan birinin gözünden anlatıyoruz.
- Konu havuzu (öncelik sırası): Napolyon'un Moskova'dan geri çekilişi 1812 (asker) · Donner Party 1846–47 (göçmen aile) ·
  Büyük Don 1709 (Avrupa köylüsü) · Valley Forge 1777–78 (asker) · Leningrad kuşatması kışı 1941–42 (sivil çocuk) ·
  Shackleton / Endurance 1915 (denizci) · Büyük Kar Fırtınası 1888 (New York) · Thames buz fuarı 1683–84 ·
  1816 "Yazsız Yıl" ve ardından gelen kış · Kara Veba kışı 1348–49
- Başlık: POV / ikinci şahıs + ünlü olay + kış tehdidi. Örn: "You're a Soldier in Napoleon's Army. Winter Is Coming."
- Anlatımda 2–3 kez karakter kameraya bakıp konuşur (vlog hissi), hikâye yine birinci ağızdan.
- Kapak: karakterin yüzü + 2–3 kelime tehdit ("-40°C", "NO FOOD", "DAY 1").

## 7. Mevsim planı
- Kış dönemi (şimdi → yaklaşık Mart): yalnızca kış bölümleri ("ünlü kışlar" serisi).
- Yaz dönemi: aynı format, sert yazlar (kuraklık, sıcak dalgası, çöl/sefer yazları). Kanal açıklaması "hardest seasons … frozen winters, scorching summers" bu yüzden iki mevsimi de kapsıyor; değiştirilmeyecek.
- Deneme: 6. veya 7. bölüm bir yaz videosu (ör. 1816 Yazsız Yıl). Kış kadar izlenirse dönüşümlü yayına geçilir. (2026-10-01, kullanıcıyla anlaşıldı: şimdilik kış devam.)
- Geçiş kademeli: yaz serisi kendi oynatma listesiyle ("Summer: How They Survived") açılır, kış listesi kanalda kalır.

## 8. Sabit kapanış çağrısı (her bölüm, 2026-10-01 kullanıcı kararı)
Son sahneden (sonraki bölüm tanıtımı) hemen önce, anlatıcının kendi sesiyle, kanal adı vermeden:
> "If you've stayed with me this far, I think this story stayed with you too. If it did, leave a like and subscribe. That's how I know you want more stories like this one — and it helps them reach more people."
- Görsel: karakter kameraya bakar ya da sakin bir mekân çekimi (lip-sync gerekmez).
- Uzunluk ~10 sn; videonun başında ya da ortasında ASLA çağrı yok.
- Kanal adı söylenmez; "subscribe" + "like" tek cümlede, yalvarmadan.

## 9. Yayın takvimi
- Haftada 2 video, saatler hedef kitleye (ABD + İspanyolca konuşan izleyici) göre (4 Ekim kararı):
  - **Çarşamba 21:10 (Türkiye)** = ABD doğu 14:10 · ABD batı 11:10 · Meksika 12:10 · İspanya 20:10 · Arjantin 15:10. Akşam yoğunluğundan 3–4 saat önce yayında olur, YouTube'un dağıtmaya zamanı kalır.
  - **Cumartesi 20:10 (Türkiye)** = ABD doğu 13:10 · ABD batı 10:10 · Meksika 11:10 · İspanya 19:10 · Arjantin 14:10. Hafta sonu izleme öğleden önce/öğlen başlar.
- Video 1 ve 2 eski saatte (18:10) yayınlandı; video 3'ten itibaren yeni saatler.
- Saat değişimi: İspanya 25 Ekim'de, ABD 1 Kasım'da kışa geçer, Türkiye geçmez. 1 Kasım'dan sonra aynı yerel saati korumak için Türkiye saati 1 saat ileri alınır (Çarşamba 22:10, Cumartesi 21:10).
- Değerlendirme: Cumartesi videolarının ilk 24 saat gösterim/izlenme sayıları karşılaştırılır; gerekirse saat tek değişkenle oynanır.
- Yükleme akışı: Gizli/Liste dışı yükle → kontrol → Planla (gün + yukarıdaki saat).

## 10. Değerlendirme eşiği: 10. video
- Kullanıcı kararı: kanalın tutup tutmadığına **10. videodan sonra** bakılır (haftada 2 → ~31 Ekim 2026).
- O zamana kadar: her Pazar analiz → bir sonraki bölümde tek bir şeyi iyileştir (başlık/kapak, ilk 30 sn, tempo).

## 11. Paketleme deneyi: "Actually" soru başlığı + parlak kapak (2026-10-02 kullanıcı kararı)
- İlham: Ink Explainer (@Inkexplainer96) — Nisan 2026 açıldı, 16 video, 109B abone; tek video
  "What Did Ancient Humans Actually Do All Day?" 10M izlenme. Basit evrensel soru + "Actually" + sarı 1–2 kelime parlak kapak.
- Deney: ep004'ten itibaren (ilk fırsatta) başlık soru formatında, örn.
  "What Did Vikings Actually Do All Winter?", "What Did Medieval Peasants Actually Eat in Winter?",
  "What Did People Actually Do During the Longest Night of the Year?"
- Kapak: açık/parlak zemin, kocaman 1–2 kelime (sarı), tek fikir; koyu-kasvetli kapakla A/B karşılaştır.
- Konsept (1. şahıs anlatıcı, kış) aynı kalır — sadece paketleme değişir. Sonucu CTR + izlenme ile ölç.
- ÖZGÜNLÜK KURALI (kullanıcı): kopya yok, şablon tekrarı yok. Ink Explainer'dan alınan şey *ilke*
  (herkesin merak ettiği basit soru + tek fikirli net kapak), kalıp değil. "Actually" en fazla arada bir.
  Her bölümde başlık kalıbı değişir (soru / meydan okuma / sayı / tezat / ikinci şahıs); kapak bizim
  guaj-resim stilimizde kalır, sadece daha aydınlık ve tek kelimelik. YouTube'un "tekrarlayan/seri üretim
  içerik" politikası açısından da her bölümün yapısı, açılışı ve görsel dili farklılaşmalı.

## 12. Yedek plan: tutmazsa uygulanacaklar (5 Ekim notu)
Kaynak: MYTHRA (@mythrafilms) — 3 videoyla ~2 haftada 64 Mn görüntüleme. Konusu fantastik kurgu; biz sadece paketlemeyi örnek alırız, tarih doğruluğu kuralı aynen kalır.
Karar: şimdilik mevcut formatla devam. 10. video değerlendirmesinde (≈31 Ekim) tutmuyorsa sırayla denenir:
1. Başlık = tek cümlelik şaşırtıcı olay (konuyu değil olayı söyle). Ör. ep005: "The Winter the Wine Froze in the Barrels", "He Had the Only Bread in a Starving Village".
2. Kapak = karakterin yakın yüzü + güçlü duygu + tek büyük nesne, çok az yazı (parlak kapak testinin sonucu da dikkate alınır).
3. Uzun bölüm denemesi: 15–20 dk tek hikâye.
4. Tutan bölüme hızlı devam ("Part 2") ile ivmeyi yakalamak.

## 13. vidIQ anahtar kelime notları (5 Ekim)
- vidIQ hesabı şu an başka bir kanala bağlı (Sunny Nest Studios); Unfrozen History bağlanınca kendi analizlerimiz (bırakma noktası, ülke, trafik) çekilecek.
- "great frost 1709": ~5.150 arama/ay, rekabet 18,9/100 (çok düşük) → ep005 için iyi; başlık/açıklama/etikette mutlaka geçsin.
- "coldest winter in history": ~4.430/ay, rekabet 24,8 → ep005 B başlığına uygun.
- Büyük fırsat: "history for sleep" ~815K/ay, rekabet 36 (en iyi skor 78,5); "boring history for sleep" 482K. Sakin anlatımlı bölümlerimiz bu kitleye uyar.
  Fikir (10. video sonrası değerlendirilecek): kendi bölümlerimizden 1–2 saatlik "Winter Survival Stories for Sleep" derlemesi (müzik/efekt kısık, kapanış CTA'ları çıkarılmış). Sadece kendi içeriğimiz → yeniden kullanılmış içerik sorunu yok.
- "history explained" son 30 günde +%41 büyüme.

## 14. vidIQ outlier taraması — kış/hayatta kalma nişi (6 Ekim)
Son 6 ay, <100K abone, uzun video. Kanal ortalamasının çok üstünde izlenenler:
| Video | Kanal (abone) | İzlenme | Kat | Süre |
|---|---|---|---|---|
| How Did Medieval Villages Survive Winter Without Heating? | Every Life Explained (5,8K) | 292K | 150x | 33 dk |
| The Darkest Things Ancient Humans Did To Survive The Cold | Primal HQ (1,8K) | 157K | 616x | 15 dk |
| How Mongols Survived −50°C Winters on the Open Steppe | The Last Hearth (84) | 19K | 76x | 20 dk |
| How Native Americans Stayed Warm on the Frozen Plains | Dark Origins (4,2K) | 66K | 51x | 23 dk |
| Why Inuit Igloos Stayed Warm in –50°C Brutal Arctic Winters | Smart Axen (4K) | 9K | 12x | 14 dk |
| How Vikings Build Winter Camps That Survived -50°C | Flint (891) | 14K | 16x | 13 dk |
| The Brutal Truth About Surviving a Victorian Winter | D-HistoryT (659) | 16K | 4x | 26 dk |
Çıkarımlar:
- Kazanan başlık kalıbı: "How [halk/grup] Survived / Stayed Warm [aşırı sayı, ör. −50°C] [yer]". Bizim ep001 ("How Medieval Peasants Survived Winter Without Heating") bu kalıpta → TO %5,4; ep002 "You're a Viking Farmer…" → %1,7. Veri aynı yönü gösteriyor.
- Karar: ana başlık (A) bundan sonra "How … Survived …" kalıbında; "You're a…" POV başlığı B/C'ye iner. Anlatım POV olarak kalır (fark yaratan dokunuşumuz).
- Süreler 13–33 dk; bizimkiler 8–9 dk. 10. video sonrası 15 dk'lık bölüm testi.
- Konu havuzu (henüz yapmadıklarımız): Moğollar (steppe, −50°C), Inuit (iglo), Plains yerlileri (bufalo postu), Viktorya dönemi Londra kışı, Buz Çağı insanları, 1709 Büyük Don (ep005).

## 15. Görsel QA — fiziksel mantık taraması (6 Ekim, ep005 dersi)
Kullanıcı 5:08'de pulluğu önden süren adamı yakaladı; küçük döşeme sayfalarında kaçmıştı.
- Son render'da **saniyede 1 kare, 400 px döşeme, zaman damgalı** tam tarama (60 sn'lik sayfalar).
- Her kişi/hayvan/alet için sor: doğru yönde mi, doğru aleti mi tutuyor (orak/çapa/pulluk), insan–hayvan–alet sırası fiziksel olarak doğru mu?
- Aynı karede iki benzer yüz → yakınlaştır, klon mu kontrol et.
- Mevsim/tarım: kışın olgun başak yok, yazın kar yok.
- Şüpheli her kare 800 px'e yakınlaştırılır; hatalı çekim `clip_range`/`clip_composite` ile kesilir.

## 16. Analytics notu (6 Ekim, 28 gün)
- 153 görüntüleme · 3,9 saat · +2 abone · 863 gösterim · TO %2,8 · ort. izleme 4:54.
- Viking: 103 izlenme, 4:18 (%43), ilk 3 gün TO %1,8; 0:30'da %61 kalıyor, sonra grafik DÜZ (orta kısımda kayıp yok).
- Medieval: 49 izlenme, 5:28 (%57,6) — çok iyi elde tutma.
- Trafik: Göz atma %70, kanal sayfası %11, önerilen %8,5, arama %6 → YouTube bizi ana sayfada deniyor.
- Sonuç: içerik/elde tutma GÜÇLÜ; darboğaz TIKLAMA (paketleme) + ilk 30 sn'deki %39 kayıp.
  → Kapak/başlık A/B testleri sürsün; her bölümde ilk 30 sn'ye en güçlü görüntü + soru; parlak yüz kapak.

## 17. ANA HEDEF (8 Ekim, kullanıcı kararı): "arşiv kanalı"
Tek seferlik viral değil; **her gün 100–300 izlenme alan, yıllarca çalışan videolar**. Hedef: 100 video, bunların 10–20'si düzenli kazanan.
- Hesap: 15 video × 200/gün ≈ 3.000/gün ≈ 90K/ay. (Para kazanma açıldığında RPM $3–6 → ayda ~$270–540; kitle masaüstü/yaşlı ABD ağırlıklıysa üst uca yakın.)
- Kaldıraçlar:
  1. **Aranan konu**: her bölüm konusu vidIQ arama hacmiyle seçilir (ör. "great frost 1709" ~5K/ay, düşük rekabet). Başlıkta aranan anahtar kelime + merak.
  2. **Açıklamanın ilk 2 satırı** hem kanca hem anahtar kelime; bölümler (chapters) her zaman.
  3. **Oynatma listeleri / seriler**: izleyici bir videodan diğerine geçsin (oturum süresi).
  4. **Eski videoları yeniden paketleme**: 30. ve 90. günde TO düşükse kapak/başlık güncelle.
  5. **İstikrar**: haftada 2 video → ~1 yılda 100.

## 18. Dış analiz notları (8 Ekim, kullanıcının paylaştığı vidIQ raporu)
- "how did medieval villages survive winter without heating" → ~47,6K/ay, rekabet 15 (çok düşük). Ep001 başlığı neredeyse birebir. A/B testi bitince soru formuna çevirmeyi değerlendir: "How Did Medieval Peasants Survive Winter Without Heating?"
- "viking winter" ~5,3K/ay (rekabet 30); "medieval peasant life" ~11,6K/ay.
- Outlier'lar (2–7K aboneli kanallar): Runic "How Did Humans Survive −40° Nights Inside a Massive Medieval Castle?" 301K; Every Life Explained 314K; "How Medieval Villages Survived Deadly Winters Without Heating in 1315?" 270K → soru formatı + somut sayı.
- "History for Sleep" hattı: mevcut bölümlerden uzun derleme = 0 kredi. Denenecek.
- Kanal ana sayfası: öne çıkan video + seri oynatma listesi kur.
- DÜZELTME: rapordaki "SUBSCRIBER 128" trafik satırı 3 aboneyle mümkün değil; Studio'da bu trafik "Göz atma özellikleri". Ayrıca yayın durmadı: Donner 10 Eki, ep005 14 Eki planlı.
- Ep006 Moğolistan olmak ZORUNDA: ep005'in son sahnesi "That story is next" diyerek Moğol bozkırını vaat ediyor. Kale/−40° konusu ep007 adayı.
