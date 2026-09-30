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
