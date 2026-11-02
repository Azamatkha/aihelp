"""Telegram albomni (bir nechta rasm/video) har biri alohida xabar qilib
yuboradi, ularda faqat umumiy media_group_id bo'ladi. Qismlarni qisqa vaqt
yig'ib turamiz va keyin BITTA guruh qilib qayta ishlaymiz."""

import logging
import threading

from django.db import connection

log = logging.getLogger(__name__)


class AlbumCollector:
    def __init__(self, delay: float = 1.5):
        self.delay = delay
        self._parts: dict[str, list] = {}
        self._timers: dict[str, threading.Timer] = {}
        self._lock = threading.Lock()

    def add(self, message, callback) -> None:
        key = f"{message.chat.id}:{message.media_group_id}"
        with self._lock:
            self._parts.setdefault(key, []).append(message)
            # Har yangi qism kelganda kutishni qaytadan boshlaymiz
            old = self._timers.get(key)
            if old:
                old.cancel()
            timer = threading.Timer(self.delay, self._flush, args=(key, callback))
            timer.daemon = True
            self._timers[key] = timer
            timer.start()

    def _flush(self, key: str, callback) -> None:
        with self._lock:
            parts = self._parts.pop(key, [])
            self._timers.pop(key, None)
        if not parts:
            return
        parts.sort(key=lambda m: m.message_id)
        try:
            callback(parts)
        except Exception:
            log.exception("Albomni qayta ishlashda xato")
        finally:
            connection.close()  # shu oqim ochgan DB ulanishini yopamiz