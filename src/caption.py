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


def build_caption(title: str, brand, price_text, product_url: str) -> str:
    lines = [f"✨ {title}"]
    if brand:
        lines.append(f"Marka: {brand}")
    if price_text:
        lines.append(f"Fiyat: {price_text}")
    lines.append("")
    lines.append(f"İncele & sipariş ver 👉 {product_url}")
    lines.append("")

    tags = random.sample(HASHTAG_POOL, k=min(4, len(HASHTAG_POOL)))
    tags.append(config.BRAND_HASHTAG)
    lines.append(" ".join(tags))

    return "\n".join(lines)
