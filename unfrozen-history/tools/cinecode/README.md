`qc.py` ve `scene_check.py`, sarpstar/cinecode (MIT, LICENSE bu klasörde) deposundan değiştirilmeden alındı; sürüm VERSION dosyasında.
Kullanım (bölüm teslimi öncesi otomatik kontrol):
  python3 tools/cinecode/qc.py all  build/ep010/ep010_en_v1.mp4      # donma, siyah, tekrar, patlama, ses
  python3 tools/cinecode/qc.py hook build/ep010/ep010_en_v1.mp4      # ilk 2 sn hareket var mı
