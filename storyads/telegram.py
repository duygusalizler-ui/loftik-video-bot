"""Sonucu Telegram'a yollar (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)."""
import os

import requests


def _api(method: str) -> str:
    return f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/{method}"


def send(res, brand) -> None:
    chat = os.environ["TELEGRAM_CHAT_ID"]
    plan = res.plan
    head = (f"🎬 TASLAK — {brand.ad} hikâye videosu (paylaşmadan önce 30 sn izle)\nFormat: {plan.get('format')} | Karakter: {plan.get('karakter')}\n"
            f"Kanca: {plan.get('kanca')}\nFinal: {plan.get('final_yazi')}")
    if res.video:
        with open(res.video, "rb") as f:
            requests.post(_api("sendVideo"), data={"chat_id": chat, "caption": head[:1000], "supports_streaming": True},
                          files={"video": f}, timeout=300).raise_for_status()
        sheet = os.path.join(os.path.dirname(res.video), "kareler.jpg")
        if os.path.exists(sheet):
            with open(sheet, "rb") as f:
                requests.post(_api("sendPhoto"), data={"chat_id": chat, "caption": "Hızlı kontrol: videodan 6 kare"},
                              files={"photo": f}, timeout=120)
        text = f"📝 AÇIKLAMA (kopyala):\n\n{res.caption}\n\n📌 SABİT YORUM:\n{res.pinned_comment}"
    else:
        text = head + "\n\n⚠️ Kalite kontrolünden yeterli sahne geçmedi, video gönderilmedi."
    gecen = sum(1 for q in res.qa_log if q.get("gecti"))
    text += f"\n\n✅ Kalite kontrolü: {gecen} geçti, {len(res.qa_log) - gecen} elendi"
    kesilen = [f"sahne {q['asama'][5:6]}: {h.get('sn')} sn {h.get('sorun')}" for q in res.qa_log
               for h in (q.get("hatali_kareler") or []) if q.get("gecti") and isinstance(h, dict)]
    if kesilen:
        text += "\n✂️ Kesilen hatalı anlar:\n" + "\n".join(kesilen[:8])
    uyarilar = [h for q in res.qa_log if q.get("asama") == "sure" for h in q.get("hatalar", [])]
    if uyarilar:
        text += "\n⚠️ " + "; ".join(uyarilar)
    requests.post(_api("sendMessage"), data={"chat_id": chat, "text": text[:4000]}, timeout=60).raise_for_status()
