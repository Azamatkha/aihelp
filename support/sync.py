"""Bot ma'lumotlarini turon-ai backendga yuborish (push).

Server bu noutbukka ulana olmaydi, lekin noutbuk serverga public tunnel orqali
chiqa oladi — shuning uchun bot o'zi davriy yuboradi:
  • userlar — har safar hammasi (soni kam);
  • xabarlar — oxirgi muvaffaqiyatli yuborishdan beri yangi yoki o'zgarganlari.
    Holat o'zgarishi (javob berildi / yopildi) doim answered_at ni qo'yadi,
    shuning uchun created_at yoki answered_at bo'yicha topish yetarli.
Backend hammasini upsert qiladi — qayta yuborish zararsiz.
"""

import json
import logging
import threading
from datetime import datetime, timedelta

import requests
from django.conf import settings
from django.db import close_old_connections
from django.db.models import Q
from django.utils import timezone

from support.models import Message, TelegramUser

log = logging.getLogger(__name__)

BATCH = 500
# Soatlar farqi / sekin tranzaksiyalar uchun zaxira
OVERLAP = timedelta(minutes=5)
STATE_FILE = settings.DATA_DIR / "sync_state.json"


def enabled() -> bool:
    return bool(settings.BACKEND_URL and settings.BACKEND_API_KEY)


def _load_since():
    try:
        value = json.loads(STATE_FILE.read_text(encoding="utf-8"))["last_success"]
        return datetime.fromisoformat(value)
    except (OSError, ValueError, KeyError):
        return None


def _save_since(moment) -> None:
    STATE_FILE.write_text(json.dumps({"last_success": moment.isoformat()}), encoding="utf-8")


def _iso(dt):
    return dt.isoformat() if dt else None


def _user_row(u: TelegramUser) -> dict:
    return {
        "telegram_id": u.telegram_id,
        "username": u.username,
        "full_name": u.full_name,
        "language": u.language,
        "phone": u.phone,
        "reg_step": u.reg_step,
        "is_banned": u.is_banned,
        "first_seen_at": _iso(u.created_at),
        "last_message_at": _iso(u.last_message_at),
    }


def _message_row(m: Message) -> dict:
    return {
        "bot_message_id": m.pk,
        "telegram_id": m.user.telegram_id,
        "direction": m.direction,
        "status": m.status,
        "content_type": m.content_type,
        "items": m.items,
        "text": m.text,
        "admin_name": m.admin_name,
        "sent_at": _iso(m.created_at),
        "answered_at": _iso(m.answered_at),
    }


def _proxies() -> dict | None:
    proxy = settings.BACKEND_PROXY
    if not proxy or proxy.lower() == "none":
        return None
    return {"http": proxy, "https": proxy}


def _post(session: requests.Session, users: list, messages: list) -> dict:
    # Proxy har so'rovga alohida beriladi: requests'da muhitdagi HTTPS_PROXY
    # session.proxies dan ustun turadi, so'rovniki esa — hammasidan.
    resp = session.post(
        f"{settings.BACKEND_URL}/v1/telegram-bot/sync",
        json={"users": users, "messages": messages},
        headers={"X-Bot-Key": settings.BACKEND_API_KEY},
        proxies=_proxies(),
        timeout=30,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def sync_once(full: bool = False) -> tuple[int, int]:
    """Bir marta yuboradi. (userlar, xabarlar) sonini qaytaradi; xatoda exception."""
    started = timezone.now()
    since = None if full else _load_since()

    users = [_user_row(u) for u in TelegramUser.objects.order_by("pk")]
    messages_qs = Message.objects.select_related("user").order_by("pk")
    if since is not None:
        since -= OVERLAP
        messages_qs = messages_qs.filter(Q(created_at__gte=since) | Q(answered_at__gte=since))
    messages = [_message_row(m) for m in messages_qs]

    sent_users = sent_messages = 0
    with requests.Session() as session:
        if settings.BACKEND_PROXY.lower() == "none":
            session.trust_env = False  # to'g'ridan-to'g'ri, tizim proxy'sini ham chetlab
        # Avval userlar — xabarlar ularga bog'lanadi
        for i in range(0, len(users), BATCH):
            sent_users += _post(session, users[i:i + BATCH], [])["users"]
        for i in range(0, len(messages), BATCH):
            sent_messages += _post(session, [], messages[i:i + BATCH])["messages"]

    _save_since(started)
    return sent_users, sent_messages


def _loop(stop: threading.Event) -> None:
    log.info("Backendga sinxronizatsiya yoqildi: %s (har %s s, proxy: %s)",
             settings.BACKEND_URL, settings.BACKEND_SYNC_INTERVAL, settings.BACKEND_PROXY or "yo'q")
    while not stop.is_set():
        close_old_connections()
        try:
            users, messages = sync_once()
            if messages:
                log.info("Sync: %s user, %s xabar yuborildi", users, messages)
        except Exception as e:  # tarmoq/tunnel uzilsa — keyingi safar qayta urinadi
            log.warning("Backendga yuborib bo'lmadi: %s: %s", type(e).__name__, e)
        finally:
            close_old_connections()
        stop.wait(max(settings.BACKEND_SYNC_INTERVAL, 10))


def start_sync_thread() -> threading.Event | None:
    """Fon thread'ini ishga tushiradi. To'xtatish uchun qaytgan Event'ni set() qiling."""
    if not enabled():
        log.info("BACKEND_URL / BACKEND_API_KEY berilmagan — backendga sinxronizatsiya o'chiq")
        return None
    stop = threading.Event()
    threading.Thread(target=_loop, args=(stop,), name="backend-sync", daemon=True).start()
    return stop
