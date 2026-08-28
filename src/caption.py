"""Telegram / Instagram için açıklama + hashtag metni üretir."""
import random

from . import config

HASHTAG_POOL = [
    "#sneaker",
    "#ayakkabı",
    "#günlükstil",
    "#ayakkabımoda",
    "#kombin",
    "#erkekmoda",
    "#kadınmoda",
    "#style",
]

# Kategori slug'ını okunabilir bir Türkçe etikete çeviriyor (bir tür "özellik" satırı).
CATEGORY_LABELS = {
    "spor-ayakkabi": "Spor Ayakkabı",
    "erkek-ayakkabi": "Erkek Ayakkabı",
    "kadin-ayakkabi": "Kadın Ayakkabı",
    "deri-ayakkabi": "Deri Ayakkabı",
}


def build_caption(title: str, brand, category_slug=None) -> str:
    lines = [f"✨ {title}"]
    if brand:
        lines.append(f"Marka: {brand}")
    label = CATEGORY_LABELS.get(category_slug)
    if label:
        lines.append(label)
    lines.append("")
    lines.append("Sipariş vermek için bio'daki linke tıkla 👆")
    lines.append("")

    tags = random.sample(HASHTAG_POOL, k=min(4, len(HASHTAG_POOL)))
    tags.append(config.BRAND_HASHTAG)
    lines.append(" ".join(tags))

    return "\n".join(lines)
