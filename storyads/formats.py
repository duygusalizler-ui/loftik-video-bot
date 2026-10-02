"""
Anlatim formatlari. Her videoda farkli bir format secilir ki hesap
"hep ayni reklam" gibi durmasin. Hepsi ayni iskelete oturur:
kanca (dikkat) -> sorun -> oneri -> urun (farkli bakis acisi) -> sonuc (mutluluk).
"""

FORMATS = {
    "rovans": {
        "ad": "Rövanş",
        "fikir": "Karakter bir şeye yenilir (kötü an). Ürünle AYNI yere/duruma geri döner ve rövanşı alır. "
                 "Ürün, rövanş anında yerden/alçak açıdan gösterilir.",
        "final_ornek": "Kış: 0 — Ayı: 1",
    },
    "saat": {
        "ad": "Saat damgası",
        "fikir": "Ekran yazıları saatle ilerler (08:30 / 13:00 / 17:45). Aynı saat başta kötü, sonda iyi. "
                 "Ürün, karakterin günü nasıl değiştirdiğiyle tanıtılır.",
        "final_ornek": "17:45 — enerji hâlâ %100",
    },
    "sirri_ne": {
        "ad": "Sırları ne?",
        "fikir": "Karakter etrafındakilerin neden mutlu/rahat olduğunu merak eder. Kamera sırrı ortaya çıkarır: "
                 "herkes aynı ürünü kullanıyor (yan yana dizilmiş ürün çekimi).",
        "final_ornek": "Artık sır değil.",
    },
    "pov": {
        "ad": "POV",
        "fikir": "'POV: ...' kancasıyla izleyiciyi karakterin yerine koyar. Ürün karakterin gözünden "
                 "(birinci şahıs kamera) görülür.",
        "final_ornek": "POV: sonunda doğru seçim",
    },
    "beklenti_gercek": {
        "ad": "Beklenti / Gerçek",
        "fikir": "Önce komik bir 'beklenti' sahnesi, sonra sert 'gerçek'. Ürün gerçeği tersine çevirir.",
        "final_ornek": "Beklenti = Gerçek",
    },
    "kucuk_kahraman": {
        "ad": "Küçük kahraman",
        "fikir": "Ürün sessiz kahramandır: karakter sorunla boğuşurken ürün olayı kurtarır. "
                 "Ürün kahraman gibi çerçevelenir (alttan çekim, ışık vurur).",
        "final_ornek": "Gerçek kahraman ayağında.",
    },
    "sayac": {
        "ad": "Sayaç",
        "fikir": "Ekranda bir sayaç: 'Islak çorap sayısı: 47'. Ürünle sayaç sıfırlanır.",
        "final_ornek": "Islak çorap: 0",
    },
}

# Animasyon karakter havuzu (hep ayni hayvan olmasin)
CHARACTERS = [
    "ayı", "aslan", "tilki", "panda", "kedi", "köpek (golden)", "penguen", "rakun", "tavşan",
    "kaplan", "zürafa", "zebra", "koala", "baykuş", "sincap", "kirpi", "su samuru", "fil",
]
