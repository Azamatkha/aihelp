"""Bot: ro'yxatdan o'tish (til + telefon), user -> admin karta,
admin javobi -> user. Hamma holat bazada saqlanadi."""

import html
import json
import logging

import telebot
from django.conf import settings
from django.utils import timezone
from telebot import apihelper, types
from telebot.apihelper import ApiTelegramException

from support import texts
from support.albums import AlbumCollector
from support.models import AdminCard, AdminState, Message, TelegramUser

log = logging.getLogger(__name__)

S = Message.Status
D = Message.Direction
Step = TelegramUser.Step

CONTENT_TYPES = [
    "text", "photo", "document", "voice", "video", "video_note",
    "audio", "sticker", "animation", "location", "contact",
]
UNSUPPORTED_TYPES = ["poll", "dice", "venue", "game"]

CONTENT_LABELS = {
    "photo": "🖼 Rasm", "video": "🎬 Video", "voice": "🎤 Ovozli xabar",
    "video_note": "⏺ Dumaloq video", "audio": "🎵 Audio", "document": "📎 Fayl",
    "sticker": "Stiker", "animation": "GIF", "location": "📍 Lokatsiya",
    "contact": "👤 Kontakt", "album": "🖼 Albom",
}

albums = AlbumCollector()


def get_bot() -> telebot.TeleBot:
    if settings.TELEGRAM_PROXY:
        apihelper.proxy = {"https": settings.TELEGRAM_PROXY}
    bot = telebot.TeleBot(settings.BOT_TOKEN, threaded=False)
    register_handlers(bot)
    return bot


def setup_commands(bot: telebot.TeleBot) -> None:
    """Telegram menyusidagi buyruqlar: userlarga /start /lang, adminlarga /pending /cancel."""
    for lang, cmds in texts.USER_COMMANDS.items():
        bot.set_my_commands([types.BotCommand(c, d) for c, d in cmds], language_code=lang)
    bot.set_my_commands([types.BotCommand(c, d) for c, d in texts.USER_COMMANDS["uz"]])
    admin_cmds = [
        types.BotCommand("pending", "Javob kutayotganlar"),
        types.BotCommand("cancel", "Javob yozishni bekor qilish"),
        types.BotCommand("yuklash", "APK ni tekshirish (yangisini — faylni shu yerga tashlang)"),
    ]
    for admin_id in settings.ADMIN_IDS:
        try:
            bot.set_my_commands(admin_cmds, scope=types.BotCommandScopeChat(admin_id))
        except ApiTelegramException:
            log.warning("Admin %s hali botga /start bosmagan", admin_id)


# ------------------------------------------------------------------ #
# Yordamchilar
# ------------------------------------------------------------------ #
def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS


def send(bot, chat_id: int, text: str, reply_to: int | None = None, **kw):
    """HTML matn yuborish. reply_to — qaysi xabarga javob qilib."""
    if reply_to:
        kw["reply_parameters"] = types.ReplyParameters(message_id=reply_to, allow_sending_without_reply=True)
    return bot.send_message(chat_id, text, parse_mode="HTML", **kw)


def upsert_user(u) -> TelegramUser:
    full_name = " ".join(p for p in (u.first_name, u.last_name) if p)
    user, _ = TelegramUser.objects.update_or_create(
        telegram_id=u.id, defaults={"username": u.username or "", "full_name": full_name}
    )
    return user


def _input_media(m):
    kw = {"caption": m.caption, "caption_entities": m.caption_entities}
    if m.content_type == "photo":
        return types.InputMediaPhoto(m.photo[-1].file_id, **kw)
    if m.content_type == "video":
        return types.InputMediaVideo(m.video.file_id, **kw)
    if m.content_type == "audio":
        return types.InputMediaAudio(m.audio.file_id, **kw)
    return types.InputMediaDocument(m.document.file_id, **kw)


def copy_to(bot, chat_id: int, msgs: list, reply_to: int | None = None) -> list[int]:
    """Bitta xabarni yoki butun albomni boshqa chatga nusxalaydi (albom
    albomligicha qoladi). Qaytaradi: yangi xabarlarning ID lari."""
    rp = types.ReplyParameters(message_id=reply_to, allow_sending_without_reply=True) if reply_to else None
    if len(msgs) == 1:
        m = msgs[0]
        return [bot.copy_message(chat_id, m.chat.id, m.message_id, reply_parameters=rp).message_id]
    sent = bot.send_media_group(chat_id, [_input_media(m) for m in msgs], reply_parameters=rp)
    return [s.message_id for s in sent]


def summarize(msgs: list) -> tuple[str, str, int]:
    """(turi, matn, fayllar soni) — bazaga yozish uchun."""
    first = msgs[0]
    text = next((m.caption for m in msgs if m.caption), None) or first.text or ""
    if not text and first.content_type == "location":
        text = f"{first.location.latitude}, {first.location.longitude}"
    elif not text and first.content_type == "contact":
        text = f"{first.contact.first_name} {first.contact.phone_number}"
    elif not text and first.content_type == "sticker":
        text = first.sticker.emoji or ""
    ctype = "album" if len(msgs) > 1 else first.content_type
    return ctype, text, len(msgs)


# ------------------------------------------------------------------ #
# Karta
# ------------------------------------------------------------------ #
def card_text(msg: Message) -> str:
    u = msg.user
    when = timezone.localtime(msg.created_at).strftime("%d.%m %H:%M")
    lines = [
        f"📩 <b>Murojaat #{msg.pk}</b> · {when}",
        f"👤 {html.escape(str(u))} · <code>{u.telegram_id}</code>",
    ]
    extra = texts.FLAGS.get(u.language, "")
    if u.phone:
        extra += f"  📞 {html.escape(u.phone)}"
    if extra.strip():
        lines.append(extra.strip())
    lines.append("")
    if msg.content_type != "text":
        label = CONTENT_LABELS.get(msg.content_type, msg.content_type)
        if msg.items > 1:
            label += f" · {msg.items} ta"
        lines.append(f"<i>[{label}]</i>")
    if msg.text:
        lines.append(html.escape(msg.text[:3000]))
    lines.append("")
    if msg.status == S.NEW:
        lines.append("⏳ <b>Javob kutilmoqda</b>")
    else:
        at = timezone.localtime(msg.answered_at).strftime("%H:%M") if msg.answered_at else ""
        icon = "✅ Javob berildi" if msg.status == S.ANSWERED else "☑️ Yopildi"
        lines.append(f"<b>{icon}</b> · {html.escape(msg.admin_name)} · {at}")
    if u.is_banned:
        lines.append("🚫 <b>User bloklangan</b>")
    return "\n".join(lines)


def card_keyboard(msg: Message) -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    if msg.status == S.NEW:
        kb.row(
            types.InlineKeyboardButton("✍️ Javob yozish", callback_data=f"r:{msg.pk}"),
            types.InlineKeyboardButton("✅ Yopish", callback_data=f"c:{msg.pk}"),
        )
    ban_text = "♻️ Blokdan chiqarish" if msg.user.is_banned else "🚫 Bloklash"
    kb.row(types.InlineKeyboardButton(ban_text, callback_data=f"b:{msg.pk}"))
    return kb


def update_cards(bot, msgs) -> None:
    """Barcha adminlardagi kartalarni yangi holatga o'tkazadi."""
    for msg in msgs:
        for card in msg.cards.filter(is_card=True):
            try:
                bot.edit_message_text(
                    card_text(msg), card.admin_chat_id, card.card_msg_id,
                    parse_mode="HTML", reply_markup=card_keyboard(msg),
                )
            except ApiTelegramException as e:
                if "not modified" not in str(e):
                    log.warning("Kartani yangilab bo'lmadi: %s", e)


def find_by_card(chat_id: int, msg_id: int) -> Message | None:
    card = (
        AdminCard.objects.select_related("message__user")
        .filter(admin_chat_id=chat_id, card_msg_id=msg_id)
        .first()
    )
    return card.message if card else None


# ------------------------------------------------------------------ #
# Ro'yxatdan o'tish
# ------------------------------------------------------------------ #
def lang_keyboard() -> types.InlineKeyboardMarkup:
    kb = types.InlineKeyboardMarkup()
    kb.row(*[types.InlineKeyboardButton(label, callback_data=f"lang:{code}") for code, label in texts.LANG_BUTTONS])
    return kb


def phone_keyboard(lang: str) -> types.ReplyKeyboardMarkup:
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.row(types.KeyboardButton(texts.t("share_phone", lang), request_contact=True))
    kb.row(types.KeyboardButton(texts.t("skip", lang)))
    return kb


def app_keyboard(lang: str) -> types.InlineKeyboardMarkup:
    """Salomlashuv xabari tagidagi «Ilovani yuklab olish» tugmasi."""
    kb = types.InlineKeyboardMarkup()
    kb.row(types.InlineKeyboardButton(texts.t("get_app", lang), callback_data="app"))
    return kb


def first_name(u) -> str:
    return u.first_name or u.username or ""


def greet(bot, chat_id: int, from_user, lang: str) -> None:
    bot.send_message(chat_id, texts.t("greeting", lang, name=first_name(from_user)),
                     reply_markup=app_keyboard(lang))


def set_user_commands(bot, user: TelegramUser) -> None:
    """Menyudagi buyruqlar izohini shu userga uning tanlagan tilida o'rnatadi."""
    cmds = texts.USER_COMMANDS.get(user.language) or texts.USER_COMMANDS["uz"]
    try:
        bot.set_my_commands([types.BotCommand(c, d) for c, d in cmds],
                            scope=types.BotCommandScopeChat(user.telegram_id))
    except ApiTelegramException as e:
        log.warning("Menyuni o'rnatib bo'lmadi (%s): %s", user.telegram_id, e)


def ask_language(bot, chat_id: int) -> None:
    bot.send_message(chat_id, texts.CHOOSE_LANG, reply_markup=lang_keyboard())


def ask_phone(bot, chat_id: int, lang: str) -> None:
    bot.send_message(chat_id, texts.t("ask_phone", lang), reply_markup=phone_keyboard(lang))


def finish_registration(bot, user: TelegramUser, m) -> None:
    user.reg_step = Step.DONE
    user.save(update_fields=["reg_step", "phone"])
    # Telefon klaviaturasini olib tashlaymiz, keyin salom + yuklab olish tugmasi
    bot.send_message(m.chat.id, texts.t("registered", user.language), reply_markup=types.ReplyKeyboardRemove())
    greet(bot, m.chat.id, m.from_user, user.language)


def continue_registration(bot, user: TelegramUser, m) -> None:
    """Ro'yxatdan o'tmagan user nima yozsa ham — qaysi bosqichda qolgan bo'lsa shuni davom ettiramiz."""
    if user.reg_step == Step.LANG or not user.language:
        ask_language(bot, m.chat.id)
        return
    lang = user.language
    if m.content_type == "contact":
        if m.contact.user_id != m.from_user.id:
            bot.send_message(m.chat.id, texts.t("not_own_phone", lang), reply_markup=phone_keyboard(lang))
            return
        phone = m.contact.phone_number
        user.phone = phone if phone.startswith("+") else f"+{phone}"
        finish_registration(bot, user, m)
    elif m.text in texts.SKIP_TEXTS:
        finish_registration(bot, user, m)
    else:
        ask_phone(bot, m.chat.id, lang)


def handle_lang(bot, c) -> None:
    code = c.data.split(":", 1)[1]
    if code not in texts.FLAGS:
        bot.answer_callback_query(c.id)
        return
    user = upsert_user(c.from_user)
    user.language = code
    if user.reg_step == Step.LANG:
        user.reg_step = Step.PHONE
    user.save(update_fields=["language", "reg_step"])
    if not is_admin(user.telegram_id):
        set_user_commands(bot, user)
    bot.answer_callback_query(c.id)
    try:
        bot.edit_message_text(texts.t("lang_saved", code), c.message.chat.id, c.message.message_id)
    except ApiTelegramException:
        pass
    if user.reg_step == Step.PHONE:
        ask_phone(bot, c.message.chat.id, code)


# ------------------------------------------------------------------ #
# Ilova (APK) yuborish
# ------------------------------------------------------------------ #
# Asosiy usul: admin APK ni botga Telegram orqali tashlaydi, bot uning file_id sini
# data/apk.json ga saqlaydi va userlarga shu file_id bilan yuboradi. Bot API o'zi 50 MB
# dan katta fayl yuklay olmaydi, lekin file_id bilan istalgan hajmdagini qayta yuboradi —
# fayl Telegram serverida turadi, har safar yuklanmaydi.
# Zaxira usul: aiapk/ papkasidagi fayl (faqat 50 MB gacha).
APK_STORE = settings.DATA_DIR / "apk.json"
BOT_UPLOAD_LIMIT = 50 * 1024 * 1024

# aiapk/ dan yuklangan fayl uchun file_id keshi.
# Kalit — (fayl yo'li, hajmi, o'zgargan vaqti): yangi APK qo'yilsa kesh o'zi eskiradi.
_apk_cache: dict[tuple, str] = {}


def stored_apk() -> dict | None:
    try:
        return json.loads(APK_STORE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def is_apk(m) -> bool:
    return m.content_type == "document" and (m.document.file_name or "").lower().endswith(".apk")


def save_apk(bot, m) -> None:
    """Admin tashlagan APK ni userlarga yuboriladigan joriy ilova qilib saqlaydi."""
    doc = m.document
    data = {
        "file_id": doc.file_id,
        "file_name": doc.file_name,
        "file_size": doc.file_size,
        "set_by": m.from_user.first_name or str(m.from_user.id),
        "set_at": timezone.localtime().strftime("%d.%m.%Y %H:%M"),
    }
    APK_STORE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    mb = (doc.file_size or 0) / 1024 / 1024
    send(bot, m.chat.id,
         f"✅ Yangi APK saqlandi: <b>{html.escape(doc.file_name)}</b> ({mb:.1f} MB).\n"
         f"Endi userlar /yuklash bosganda shu fayl yuboriladi. Tekshirish: /yuklash",
         reply_to=m.message_id)


def latest_apk():
    """aiapk/ ichidagi eng yangi .apk fayl (yo'q bo'lsa — None)."""
    folder = settings.APK_DIR
    if not folder.is_dir():
        return None
    apks = [p for p in folder.iterdir() if p.is_file() and p.suffix.lower() == ".apk"]
    return max(apks, key=lambda p: p.stat().st_mtime, default=None)


def send_apk(bot, chat_id: int, lang: str | None) -> None:
    caption = texts.t("apk_caption", lang)
    stored = stored_apk()
    if stored:
        try:
            bot.send_document(chat_id, stored["file_id"], caption=caption, parse_mode="HTML")
            return
        except ApiTelegramException as e:
            log.error("Saqlangan APK (file_id) yuborilmadi, papkadan urinamiz: %s", e)

    apk = latest_apk()
    if apk is None:
        log.warning("APK yo'q: adminlar botga .apk tashlamagan, %s papkasi ham bo'sh", settings.APK_DIR)
        bot.send_message(chat_id, texts.t("apk_missing", lang))
        return
    if apk.stat().st_size > BOT_UPLOAD_LIMIT:
        log.error("%s 50 MB dan katta — bot uni yuklay olmaydi. Admin APK ni botga "
                  "Telegram orqali tashlashi kerak.", apk.name)
        bot.send_message(chat_id, texts.t("apk_missing", lang))
        return

    st = apk.stat()
    key = (str(apk), st.st_size, st.st_mtime)
    if key in _apk_cache:
        try:
            bot.send_document(chat_id, _apk_cache[key], caption=caption, parse_mode="HTML")
            return
        except ApiTelegramException:
            _apk_cache.pop(key, None)  # file_id eskirgan — qaytadan yuklaymiz
    bot.send_chat_action(chat_id, "upload_document")
    with apk.open("rb") as f:
        sent = bot.send_document(chat_id, f, caption=caption, parse_mode="HTML",
                                 visible_file_name=apk.name, timeout=300)
    _apk_cache[key] = sent.document.file_id


def request_apk(bot, chat_id: int, from_user) -> None:
    """Buyruq, menyu yoki tugma orqali kelgan so'rov — bloklanganga yubormaymiz."""
    user = upsert_user(from_user)
    if user.is_banned:
        bot.send_message(chat_id, texts.t("banned", user.language))
        return
    try:
        send_apk(bot, chat_id, user.language)
    except Exception:
        log.exception("APK yuborishda xato")
        bot.send_message(chat_id, texts.t("apk_missing", user.language))


# ------------------------------------------------------------------ #
# User -> admin
# ------------------------------------------------------------------ #
def handle_user(bot, msgs: list) -> None:
    first = msgs[0]
    user = upsert_user(first.from_user)
    if user.is_banned:
        bot.send_message(first.chat.id, texts.t("banned", user.language))
        return
    if user.reg_step != Step.DONE:
        continue_registration(bot, user, first)
        return

    had_pending = user.messages.filter(direction=D.IN, status=S.NEW).exists()
    ctype, text, count = summarize(msgs)
    msg = Message.objects.create(
        user=user, direction=D.IN, status=S.NEW, content_type=ctype,
        text=text, items=count, user_msg_id=first.message_id,
    )
    TelegramUser.objects.filter(pk=user.pk).update(last_message_at=timezone.now())

    for admin_id in settings.ADMIN_IDS:
        try:
            reply_to = None
            if ctype != "text":
                # Avval media (albom bo'lsa — albomligicha), karta unga reply bo'ladi
                ids = copy_to(bot, admin_id, msgs)
                AdminCard.objects.bulk_create(
                    [AdminCard(message=msg, admin_chat_id=admin_id, card_msg_id=i, is_card=False) for i in ids]
                )
                reply_to = ids[0]
            card = send(bot, admin_id, card_text(msg), reply_to=reply_to, reply_markup=card_keyboard(msg))
            AdminCard.objects.create(message=msg, admin_chat_id=admin_id, card_msg_id=card.message_id)
        except ApiTelegramException as e:
            log.error("Admin %s ga yuborib bo'lmadi: %s", admin_id, e)

    # Ketma-ket yozsa, "qabul qilindi" faqat bir marta
    if not had_pending:
        send(bot, first.chat.id, texts.t("received", user.language), reply_to=first.message_id)


# ------------------------------------------------------------------ #
# Admin -> user
# ------------------------------------------------------------------ #
def handle_admin(bot, msgs: list) -> None:
    first = msgs[0]
    target = None
    # 1-usul: kartaga (yoki media nusxasiga) Telegram'da Reply
    if first.reply_to_message:
        target = find_by_card(first.chat.id, first.reply_to_message.message_id)
    # 2-usul: avval "✍️ Javob yozish" bosilgan
    if target is None:
        state = AdminState.objects.select_related("reply_to__user").filter(admin_id=first.from_user.id).first()
        target = state.reply_to if state else None
    # Hech kimga javob emas, shunchaki .apk tashlandi — bu yangi ilova versiyasi
    if target is None and len(msgs) == 1 and is_apk(first):
        save_apk(bot, first)
        return
    if target is None:
        send(
            bot, first.chat.id,
            "Kimga javob? Kartadagi <b>✍️ Javob yozish</b> tugmasini bosing "
            "yoki kartaga <b>Reply</b> qilib yozing.",
            reply_to=first.message_id,
        )
        return
    send_answer(bot, msgs, target)


def send_answer(bot, msgs: list, target: Message) -> None:
    first = msgs[0]
    user = target.user
    admin_name = first.from_user.first_name or "Admin"
    try:
        copy_to(bot, user.telegram_id, msgs, reply_to=target.user_msg_id)
        delivered = True
    except ApiTelegramException as e:
        log.warning("Userga yetmadi: %s", e)
        delivered = False

    ctype, text, count = summarize(msgs)
    Message.objects.create(
        user=user, direction=D.OUT, status=S.SENT if delivered else S.FAILED,
        content_type=ctype, text=text, items=count, admin_name=admin_name,
    )
    # Bitta bosish = bitta javob (adashib boshqa xabar ketib qolmasin)
    AdminState.objects.filter(admin_id=first.from_user.id).update(reply_to=None)

    if not delivered:
        send(bot, first.chat.id, "⚠️ Javob yetkazilmadi — user botni bloklagan bo'lishi mumkin.",
             reply_to=first.message_id)
        return

    # Userning javob kutayotgan BARCHA xabarlari yopiladi
    now = timezone.now()
    pending = list(user.messages.filter(direction=D.IN, status=S.NEW))
    Message.objects.filter(pk__in=[p.pk for p in pending]).update(
        status=S.ANSWERED, answered_at=now, admin_name=admin_name
    )
    for p in pending:
        p.status, p.answered_at, p.admin_name = S.ANSWERED, now, admin_name
    update_cards(bot, pending)
    send(bot, first.chat.id, f"✅ Javob yuborildi: {html.escape(str(user))}", reply_to=first.message_id)


def handle_callback(bot, c) -> None:
    if c.data.startswith("lang:"):
        handle_lang(bot, c)
        return
    if c.data == "app":
        bot.answer_callback_query(c.id)
        request_apk(bot, c.message.chat.id, c.from_user)
        return
    if not is_admin(c.from_user.id):
        bot.answer_callback_query(c.id)
        return
    action, _, arg = c.data.partition(":")
    msg = Message.objects.select_related("user").filter(pk=arg).first() if arg.isdigit() else None
    if msg is None:
        bot.answer_callback_query(c.id, "Xabar topilmadi")
        return

    if action == "r":
        AdminState.objects.update_or_create(admin_id=c.from_user.id, defaults={"reply_to": msg})
        bot.answer_callback_query(c.id)
        send(
            bot, c.message.chat.id,
            f"✍️ <b>{html.escape(str(msg.user))}</b> ga javobingizni yozing "
            f"(matn, rasm, albom, fayl, ovoz...).\n/cancel — bekor qilish",
            reply_to=c.message.message_id,
        )
    elif action == "c":
        updated = Message.objects.filter(pk=msg.pk, status=S.NEW).update(
            status=S.CLOSED, answered_at=timezone.now(), admin_name=c.from_user.first_name or "Admin"
        )
        msg.refresh_from_db()
        update_cards(bot, [msg])
        bot.answer_callback_query(c.id, "Yopildi" if updated else "Allaqachon yopilgan")
    elif action == "b":
        user = msg.user
        user.is_banned = not user.is_banned
        user.save(update_fields=["is_banned"])
        update_cards(bot, [msg])
        bot.answer_callback_query(c.id, "Bloklandi" if user.is_banned else "Blokdan chiqarildi")


# ------------------------------------------------------------------ #
# Handlerlarni ro'yxatdan o'tkazish (birinchi mos kelgani ishlaydi)
# ------------------------------------------------------------------ #
def register_handlers(bot: telebot.TeleBot) -> None:
    def private(m):
        return m.chat.type == "private"

    def admin_only(m):
        return private(m) and is_admin(m.from_user.id)

    def user_only(m):
        return private(m) and not is_admin(m.from_user.id)

    @bot.message_handler(commands=["start"], func=private)
    def _start(m):
        if is_admin(m.from_user.id):
            send(bot, m.chat.id,
                 "👋 Siz adminsiz. Murojaatlar shu yerga keladi.\n\n"
                 "/pending — javob kutayotganlar\n/cancel — javob yozishni bekor qilish\n"
                 "/yuklash — userlarga ketadigan APK ni tekshirish\n\n"
                 "📲 Yangi APK: faylni shu chatga tashlang (Reply qilmasdan) — userlarga shu yuboriladi.")
            return
        user = upsert_user(m.from_user)
        if user.reg_step == Step.DONE:
            set_user_commands(bot, user)
            greet(bot, m.chat.id, m.from_user, user.language)
        else:
            continue_registration(bot, user, m)

    @bot.message_handler(commands=["lang"], func=user_only)
    def _lang(m):
        upsert_user(m.from_user)
        ask_language(bot, m.chat.id)

    # Ilova: /yuklash (menyuda), /app, /apk yoki eski klaviatura tugmasi. Adminlarga
    # karta bo'lib ketmasligi uchun umumiy _message handleridan OLDIN turishi shart.
    @bot.message_handler(commands=["yuklash", "app", "apk"], func=private)
    @bot.message_handler(func=lambda m: private(m) and m.text in texts.GET_APP_TEXTS)
    def _app(m):
        request_apk(bot, m.chat.id, m.from_user)

    @bot.message_handler(commands=["cancel"], func=admin_only)
    def _cancel(m):
        AdminState.objects.filter(admin_id=m.from_user.id).update(reply_to=None)
        send(bot, m.chat.id, "Bekor qilindi.")

    @bot.message_handler(commands=["pending"], func=admin_only)
    def _pending(m):
        qs = Message.objects.select_related("user").filter(direction=D.IN, status=S.NEW).order_by("created_at")
        total = qs.count()
        if not total:
            send(bot, m.chat.id, "🎉 Javob kutayotgan murojaat yo'q.")
            return
        lines = []
        for x in qs[:20]:
            preview = html.escape(x.text[:60]) or CONTENT_LABELS.get(x.content_type, x.content_type)
            lines.append(f"#{x.pk} · {html.escape(str(x.user))}: {preview}")
        send(bot, m.chat.id, f"⏳ <b>Javob kutayotganlar: {total}</b>\n\n" + "\n".join(lines))

    @bot.message_handler(content_types=CONTENT_TYPES, func=private)
    def _message(m):
        if is_admin(m.from_user.id):
            handler = lambda msgs: handle_admin(bot, msgs)  # noqa: E731
        else:
            handler = lambda msgs: handle_user(bot, msgs)  # noqa: E731
        try:
            if m.media_group_id:
                albums.add(m, handler)  # albom — qismlar yig'ilgach bir martada
            else:
                handler([m])
        except Exception:
            log.exception("Xabarni qayta ishlashda xato")

    @bot.message_handler(content_types=UNSUPPORTED_TYPES, func=user_only)
    def _unsupported(m):
        user = upsert_user(m.from_user)
        bot.send_message(m.chat.id, texts.t("unsupported", user.language))

    @bot.callback_query_handler(func=lambda c: True)
    def _callback(c):
        try:
            handle_callback(bot, c)
        except Exception:
            log.exception("Tugmani qayta ishlashda xato")