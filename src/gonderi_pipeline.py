"""
"gonderi" modu -- trendnora tarzi kaydirmali (carousel) Instagram gonderisi.

Video uretmez. Sitedeki gercek urun fotograflarini REFERANS alarak Gemini ile
ayni sik studyo sahnesinde, farkli acilardan 4:5 urun gorselleri uretir:

  1. Cift ayakkabi, 3/4 on aci (kapak karesi)
  2. Tek ayakkabi, yandan profil
  3. Arkadan / ustten aci
  4. Yakin detay (malzeme, dikis, taban)

Her kare sitedeki gercek fotografla karsilastirilir (quality_check, studyo
icin ayri kriterlerle). Gecemeyen kare yeniden uretilir; yine gecemezse
atlanir. Urunu degistiren (renk, taban, toka, logo) kare ASLA gonderilmez.

Bot sezonunda (config.boots_enabled) sahneye kislik aksesuarlar eklenir.
"""
from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageOps

from . import config, quality_check
from .gemini_video import QuotaExceededError

POST_SIZE = (1080, 1350)  # Instagram 4:5

BASE_SET = (
    "Bright, clean product photo for an Instagram shoe store, shot in a real photo studio: "
    "white Carrara marble tabletop, soft natural daylight from a window on the left with gentle "
    "palm-leaf shadows falling on the back wall and the tabletop only -- NO leaf shadows across "
    "the shoes themselves, the shoes are evenly and clearly lit so their true color and material "
    "are easy to see. Light neutral background wall, crisp focus on the shoes, realistic soft "
    "contact shadows under the soles."
)
WINTER_PROPS = (
    " Cozy winter mood: a folded chunky cream knit scarf and two pine cones placed beside the "
    "shoes, a few tiny sprigs of fir; warm but still bright and airy light."
)
SEASON_PROPS = " A small potted green plant softly out of focus in the background."

ANGLES = [
    ("kapak", "A PAIR of the shoes: one shoe in front at a three-quarter front angle, the second "
              "shoe slightly behind and turned the other way, both fully visible, filling most of the frame."),
    ("yan", "A PAIR of the shoes in a clean side profile view: one shoe in front pointing left showing "
            "its full outer side and sole edge, the second shoe right behind it, slightly offset, also "
            "pointing left, both clearly visible and large in the frame."),
    ("on", "A PAIR of the shoes standing side by side, seen straight from the front at a slightly "
           "low eye-level angle, toes pointing toward the camera, both fully visible and large."),
    ("capraz", "A PAIR of the shoes at a three-quarter front angle from the other side, both pointing "
               "right, one slightly in front of the other, toes, sides and soles clearly visible."),
    ("genis", "A PAIR of the shoes placed a little further from the camera in a wider shot that shows "
              "more of the styled studio scene, both shoes at a three-quarter front angle, still the clear "
              "main subject."),
    ("detay", "A closer shot of a PAIR of the shoes at a low front angle: one shoe sharp in the "
              "foreground showing material texture, stitching and sole, the second shoe right beside "
              "it slightly softer; both shoes visible in the frame."),
]

RULES = (
    " The shoes MUST be EXACTLY the product in the reference photos: same model and shape, same "
    "upper color and material (leather vs suede vs fabric), same sole color and thickness, same "
    "laces / buckles / zips / fur lining / stitching, same shaft height. Do not redesign anything. "
    "Keep the EXACT color of the reference under the studio light: black stays a true deep black "
    "(never charcoal, grey or brown), white stays clean white, beige/sand keeps its exact tone -- "
    "the warm daylight must not shift the product color. "
    "Do NOT invent parts that are not clearly visible in the reference photos: no extra pull tabs, "
    "loops, rings, straps, buckles, logos or seams -- where a part is not visible in the references "
    "(e.g. the back of the heel), keep it plain and simple. "
    "Material texture must be true to life: suede looks soft, matte and slightly napped with visible "
    "fibers (never smooth canvas or fabric); leather shows natural grain and a gentle sheen. "
    "NO feet, NO legs, NO people, NO hands. NO text, NO letters, NO logos, NO brand names, NO price "
    "tags anywhere in the scene (also not on boxes, books or props). If the product itself has its "
    "own small logo, number or print in the reference, keep it in the same place, same size and "
    "color, simple and clean -- never erase it and never add a new one. ALWAYS show exactly TWO shoes (one pair, a left and a right shoe) -- never a single shoe, never more than two. "
    "Vertical 4:5 composition. Photorealistic, like a real professional e-commerce photo: no "
    "surreal elements, no melting shapes, no duplicated or floating objects."
)

QA_PROMPT_STUDIO = """Sen bir e-ticaret ürün fotoğrafı kalite kontrolcüsüsün.
İLK görsel: sitedeki GERÇEK ürün fotoğrafı (referans).
SONRAKİ görsel: yapay zekâyla üretilmiş stüdyo ürün fotoğrafı (Instagram gönderisi için).

Üretilen görseldeki ayakkabıyı referansla karşılaştır:
1. Model/şekil aynı mı (burun, bilek/konç yüksekliği, bağcık/toka/fermuar/lastik, topuk)?
2. Renkler ve malzeme aynı mı (üst malzeme, süet/deri farkı, astar/kürk, TABAN rengi ve kalınlığı)?
3. Uydurma logo, yazı, desen, fiyat etiketi eklenmiş mi (ürünün üstünde veya sahnede)?
4. Ayak, bacak, el veya insan var mı? Karede TAM OLARAK bir çift (iki ayakkabı: bir sol, bir sağ) var mı?
5. Yapay zekâ hatası var mı (eriyen/bozuk şekiller, çift ya da havada duran nesneler, saçma detaylar)?
Stüdyo ışığı ve temiz/şık sahne BURADA HATA DEĞİL, istenen şey budur.
Referansta görünmeyen bir bölgeyi (ör. topuk arkası) sade göstermek hata değildir; ama referansta
olmayan belirgin bir parça (çekme kulpu, halka, toka, logo) eklenmişse bu hatadır.

Sadece şu JSON'u döndür:
{"urun_benzerligi": 0-10, "gercekcilik": 0-10, "hatalar": ["kısa Türkçe madde"], "puan": 0-10}
"puan" = en düşük kritik değer. Taban rengi, ana renk veya model farklıysa puan en fazla 4.
Yazı/logo varsa veya ayak/insan varsa puan en fazla 4.
Karede tek ayakkabı varsa, ikiden fazla ayakkabı varsa ya da iki ayakkabı da aynı ayağa aitse puan en fazla 4.
Malzeme açıkça farklı bir malzemeye dönüşmüşse (ör. süet belirgin şekilde örgü/kanvas kumaş gibiyse) veya ürünün üstüne düşen
gölgeler rengini/dokusunu gizliyorsa puan en fazla 6.
Renk tonu kaymışsa (ör. siyah ürün kahverengi/füme/gri görünüyorsa, bej daha soluk ya da daha koyuysa)
puan en fazla 6.
"""


def _client():
    from google import genai

    if not config.GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY tanımlı değil (GitHub Secrets'a eklemeyi unutma).")
    return genai.Client(api_key=config.GEMINI_API_KEY)


def _mime(path: str) -> str:
    return "image/png" if path.lower().endswith(".png") else "image/jpeg"


def _to_post(path: str) -> str:
    img = Image.open(path).convert("RGB")
    img = ImageOps.fit(img, POST_SIZE, method=Image.LANCZOS, centering=(0.5, 0.55))
    out = str(Path(path).with_suffix(".4x5.jpg"))
    img.save(out, quality=93)
    return out


def scene_prompt(angle_prompt: str, winter: bool) -> str:
    return BASE_SET + (WINTER_PROPS if winter else SEASON_PROPS) + " " + angle_prompt


def generate_post_image(refs: list, prompt: str, out_path: str, product_title: str = "") -> str:
    from google.genai import types

    client = _client()
    parts = [types.Part.from_bytes(data=Path(r).read_bytes(), mime_type=_mime(r)) for r in refs]
    if product_title:
        parts.append(
            f"The product is: {product_title}. The {len(refs)} reference photo(s) show this SAME exact "
            "product (sometimes worn on a foot) -- copy the shoe itself exactly, never the foot. "
        )
    parts.append(prompt + RULES)
    cfg_kwargs = {"response_modalities": ["TEXT", "IMAGE"]}
    try:
        cfg = types.GenerateContentConfig(**cfg_kwargs, image_config=types.ImageConfig(aspect_ratio="4:5"))
    except Exception:  # noqa: BLE001 -- eski SDK'da image_config yoksa
        cfg = types.GenerateContentConfig(**cfg_kwargs)
    resp = None
    for model in dict.fromkeys([config.GEMINI_IMAGE_MODEL, "gemini-3-pro-image", "gemini-2.5-flash-image"]):
        try:
            resp = client.models.generate_content(model=model, contents=parts, config=cfg)
            break
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            if "429" in msg or "RESOURCE_EXHAUSTED" in msg:
                raise QuotaExceededError(f"Gemini görsel kotası doldu: {exc}") from exc
            if "404" in msg or "NOT_FOUND" in msg:
                print(f"UYARI: görsel modeli '{model}' kullanılamıyor, sıradaki deneniyor.")
                continue
            raise
    if resp is None:
        raise RuntimeError("Kullanılabilir Gemini görsel modeli bulunamadı.")
    for part in resp.candidates[0].content.parts:
        inline = getattr(part, "inline_data", None)
        if inline is not None and getattr(inline, "data", None):
            Path(out_path).write_bytes(inline.data)
            return _to_post(out_path)
    raise RuntimeError("Gemini ürün görseli döndürmedi.")


def _try_angle(refs, reference_path, name, angle, winter, work, tag, attempts, product_title, qa_log):
    prompt = scene_prompt(angle, winter)
    for attempt in range(1, attempts + 1):
        try:
            print(f"Gönderi karesi '{name}': görsel üretiliyor (deneme {tag}{attempt})...")
            img = generate_post_image(refs, prompt, os.path.join(work, f"{name}_{tag}{attempt}.png"), product_title)
        except QuotaExceededError:
            raise
        except Exception as exc:  # noqa: BLE001
            print(f"UYARI: kare üretilemedi: {exc}")
            continue
        qa = quality_check.safe_score(reference_path, [img], QA_PROMPT_STUDIO)
        qa_log.append({"asama": name, "deneme": f"{tag}{attempt}", **qa})
        print(f"  kalite puanı: {qa['puan']}/10 {qa.get('hatalar') or ''}")
        if qa["gecti"]:
            return img
    return None


def build_post(product, reference_path: str, extra_refs: list, winter: bool, work: str) -> tuple[list, list]:
    """Kalite kontrolunden gecen gorsellerin yollari + qa kaydi dondurur.

    Acilar sirayla denenir; TARGET_POST_IMAGES (varsayilan 4) kare gecince durulur,
    sonraki acilar sadece yedektir. Once her aci bir kez (SCENE_IMAGE_ATTEMPTS denemeyle) uretilir; en az
    MIN_POST_IMAGES kareye ulasilamazsa basarisiz acilara POST_EXTRA_ATTEMPTS
    kadar ek deneme verilir. Kare sirasi her zaman ANGLES sirasidir (kapak once).
    """
    os.makedirs(work, exist_ok=True)
    refs = [reference_path] + list(extra_refs or [])[:3]
    angles = ANGLES[: config.POST_ANGLES]
    passed: dict = {}
    qa_log: list = []
    target = max(config.MIN_POST_IMAGES, min(config.TARGET_POST_IMAGES, len(angles)))
    for name, angle in angles:
        if len(passed) >= target:
            break  # hedefe ulasildi; kalan acilar sadece yedekti
        img = _try_angle(refs, reference_path, name, angle, winter, work, "", config.POST_ANGLE_ATTEMPTS,
                         product.title, qa_log)
        if img:
            passed[name] = img
    # En az MIN_POST_IMAGES kareye tamamla: once gecemeyen acilar tekrar denenir,
    # sonra bu urunde ise yarayan acilarin farkli bir varyanti uretilir (urun ATILMAZ).
    extra_left = config.POST_EXTRA_ATTEMPTS
    variant = 0
    while len(passed) < config.MIN_POST_IMAGES and extra_left > 0:
        missing = [(n, a) for n, a in angles if n not in passed]
        working = [(n, a) for n, a in angles if n in passed and not n.endswith("_v")]
        pool = missing + [(f"{n}_v{variant}", a) for n, a in working]
        variant += 1
        for name, angle in pool:
            if extra_left <= 0 or len(passed) >= config.MIN_POST_IMAGES:
                break
            extra_left -= 1
            img = _try_angle(refs, reference_path, name, angle, winter, work, "ek", 1, product.title, qa_log)
            if img:
                passed[name] = img
    order = [n for n, _ in angles]
    images = [passed[n] for n in sorted(passed, key=lambda k: (order.index(k.split("_v")[0]), k))]
    return images, qa_log


def qa_summary(images: list, qa_log: list) -> str:
    failed = [q for q in qa_log if not q.get("gecti")]
    lines = [
        f"✅ {len(images)} kare kalite kontrolünden geçti "
        f"(eşik {config.QA_MIN_SCORE}/10, {len(failed)} deneme elendi)"
    ]
    for q in failed[:4]:
        err = "; ".join(q.get("hatalar") or [])[:120]
        lines.append(f"• {q['asama']} deneme {q['deneme']}: {q['puan']}/10 {err}")
    return "\n".join(lines)
