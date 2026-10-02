"""
storyads -- markadan bagimsiz "hikayeli reklam" motoru.

Bir urun linki + marka ayari (brands/<marka>.json) verilir; motor:
  1. urunu sayfadan okur (ad, fiyat, gercek fotograflar)
  2. Gemini ile hikaye plani yazar: kanca -> sorun -> oneri -> urun -> sonuc
     (her seferinde farkli anlatim formati ve karakter)
  3. her sahne icin gorsel (animasyon karakter + gercekci arka plan +
     GERCEK gibi duran urun) ve ses efektli video klibi uretir
  4. kalite kontrolunden gecmeyeni yeniden uretir
  5. yumusak gecisli kurgu + ekran yazilari + kisik muzik
  6. aciklama metni (bio/site yonlendirmeli), sabit yorum, hashtag

Loftik ilk marka; yeni musteri = yeni bir brands/*.json dosyasi.
"""
