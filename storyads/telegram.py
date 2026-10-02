"""Sonucu Telegram'a yollar (TELEGRAM_BOT_TOKEN + TELEGRAM_CHAT_ID)."""
import os

import requests


def _api(method: str) -> str:
    return f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/{method}"


def send(res, brand) -> None:
    chat = os.environ["TELEGRAM_CHAT_ID"]
    plan = res.plan
    head = (f"🎬 {brand.ad} — hikâye videosu\nFormat: {plan.get('format')} | Karakter: {plan.get('karakter')}\n"
            f"Kanca: {plan.get('kanca')}\nFinal: {plan.get('final_yazi')}")
    if res.video:
        with open(res.video, "rb") as f:
            requests.post(_api("sendVideo"), data={"chat_id": chat, "caption": head[:1000], "supports_streaming": True},
                          files={"video": f}, timeout=300).raise_for_status()
        text = f"📝 AÇIKLAMA (kopyala):\n\n{res.caption}\n\n📌 SABİT YORUM:\n{res.pinned_comment}"
    else:
        text = head + "\n\n⚠️ Kalite kontrolünden yeterli sahne geçmedi, video gönderilmedi."
    gecen = sum(1 for q in res.qa_log if q.get("gecti"))
    text += f"\n\n✅ Kalite kontrolü: {gecen} geçti, {len(res.qa_log) - gecen} elendi"
    requests.post(_api("sendMessage"), data={"chat_id": chat, "text": text[:4000]}, timeout=60).raise_for_status()
