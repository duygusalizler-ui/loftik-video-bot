"""Telegram / Instagram için açıklama + hashtag metni üretir."""
import random

from . import config

# Cinsiyet-nötr etiketler (her ürün için kullanılabilir)
NEUTRAL_HASHTAGS = ["#sneaker", "#ayakkabı", "#günlükstil", "#ayakkabımoda", "#kombin", "#style"]
MALE_HASHTAGS = ["#erkekmoda", "#erkekayakkabı", "#erkekstil"]
FEMALE_HASHTAGS = ["#kadınmoda", "#kadınayakkabı", "#kadınstil"]

# Kategori slug'ını okunabilir bir Türkçe etikete çeviriyor (bir tür "özellik" satırı).
CATEGORY_LABELS = {
    "spor-ayakkabi": "Spor Ayakkabı",
    "erkek-ayakkabi": "Erkek Ayakkabı",
    "kadin-ayakkabi": "Kadın Ayakkabı",
    "deri-ayakkabi": "Deri Ayakkabı",
}

# Chekich'ten bulunan gerçek malzeme/astar/topuk bilgisini her seferinde
# FARKLI bir cümle kalıbıyla anlatmak için -- bilgiler değişmiyor, sadece
# anlatım şekli değişiyor. Hiçbir kalıp yeni bir özellik uydurmuyor.
SPEC_TEMPLATES = [
    "{material} kullanılarak üretildi, iç kısmında {lining} astar var, topuk yüksekliği {heel}.",
    "Malzemesi {material}; astarı {lining}; topuğu {heel} yükseklikte.",
    "{heel} topuk ile rahat bir kullanım sunuyor. Dış yüzeyi {material}, iç astarı {lining}.",
    "İçi {lining} astarlı, dışı {material}. Topuk yüksekliği {heel}.",
    "{material} üzerine {lining} iç astar ve {heel} topuk detayına sahip.",
    "Dış malzeme {material}, iç astar {lining}, topuk {heel}.",
]


def build_spec_line(specs) -> str | None:
    """specs: chekich.ChekichSpecs veya None. Eksik alan varsa uygun kelimeyle atlar."""
    if specs is None:
        return None
    if not (specs.material or specs.lining or specs.heel_height):
        return None
    material = specs.material or "kaliteli malzeme"
    lining = specs.lining or "yumuşak astar"
    heel = specs.heel_height or "standart yükseklikte"
    template = random.choice(SPEC_TEMPLATES)
    return template.format(material=material, lining=lining, heel=heel)


def _detect_gender(title: str, category_slug) -> str:
    combined = f"{title} {category_slug or ''}".upper()
    has_male = "ERKEK" in combined
    has_female = "KADIN" in combined
    if has_male and not has_female:
        return "male"
    if has_female and not has_male:
        return "female"
    return "neutral"


# Instagram artik gonderi basina en fazla 5 hashtag kabul ediyor (marka etiketi dahil).
MAX_HASHTAGS = 5


def _product_tags(title: str, category_slug) -> list:
    """Urunun turune ozel, en cok aranan etiketler (en spesifik once)."""
    t = f"{title} {category_slug or ''}".lower()
    gender = _detect_gender(title, category_slug)
    tags = []
    if "bot" in t.split() or category_slug == "bot" or " bot " in f" {t} ":
        tags.append({"male": "#erkekbot", "female": "#kadınbot"}.get(gender, "#bot"))
        tags.append("#kışlıkbot")
    elif "spor" in t or "sneaker" in t:
        tags += ["#sporayakkabı", "#sneaker"]
    elif "deri" in t or category_slug == "deri-ayakkabi":
        tags.append("#deriayakkabı")
    if gender == "male":
        tags.append("#erkekayakkabı")
    elif gender == "female":
        tags.append("#kadınayakkabı")
    return tags


def _hashtags_for(title: str, category_slug) -> list:
    """Marka etiketi haric en fazla MAX_HASHTAGS-1 etiket: once urune ozel, kalan genel."""
    slots = MAX_HASHTAGS - 1
    tags = list(dict.fromkeys(_product_tags(title, category_slug)))[:slots]
    gender = _detect_gender(title, category_slug)
    pool = NEUTRAL_HASHTAGS + (MALE_HASHTAGS if gender == "male" else FEMALE_HASHTAGS if gender == "female" else [])
    pool = [p for p in pool if p not in tags]
    tags += random.sample(pool, k=max(0, min(slots - len(tags), len(pool))))
    return tags


def build_caption(title: str, brand, category_slug=None, spec_line: str | None = None) -> str:
    lines = [f"✨ {title}"]
    if brand:
        lines.append(f"Marka: {brand}")
    label = CATEGORY_LABELS.get(category_slug)
    if label:
        lines.append(label)
    if spec_line:
        lines.append(spec_line)
    lines.append("")
    lines.append("Sipariş vermek için bio'daki linke tıkla 👆")
    lines.append("")

    tags = _hashtags_for(title, category_slug)
    tags.append(config.BRAND_HASHTAG)
    lines.append(" ".join(tags))

    return "\n".join(lines)
