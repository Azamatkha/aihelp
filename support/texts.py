"""Foydalanuvchiga ko'rinadigan matnlar. Admin tomoni — o'zbekcha, bot.py da."""

FLAGS = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧"}
LANG_BUTTONS = [("uz", "🇺🇿 O'zbekcha"), ("ru", "🇷🇺 Русский"), ("en", "🇬🇧 English")]

CHOOSE_LANG = "🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык\n🇬🇧 Choose your language"

TEXTS = {
    "ask_phone": {
        "uz": "📱 Telefon raqamingizni yuboring — kerak bo'lsa siz bilan bog'lanamiz.\n"
              "Pastdagi tugmani bosing yoki o'tkazib yuboring.",
        "ru": "📱 Отправьте номер телефона — при необходимости мы с вами свяжемся.\n"
              "Нажмите кнопку ниже или пропустите.",
        "en": "📱 Share your phone number so we can contact you if needed.\n"
              "Tap the button below or skip.",
    },
    "share_phone": {"uz": "📱 Raqamni yuborish", "ru": "📱 Отправить номер", "en": "📱 Share number"},
    "skip": {"uz": "⏭ O'tkazib yuborish", "ru": "⏭ Пропустить", "en": "⏭ Skip"},
    "not_own_phone": {
        "uz": "Iltimos, o'zingizning raqamingizni tugma orqali yuboring.",
        "ru": "Пожалуйста, отправьте свой номер с помощью кнопки.",
        "en": "Please share your own number using the button.",
    },
    "welcome": {
        "uz": "✅ Tayyor! Endi muammo yoki savolingizni yozing — matn, rasm, video yoki ovozli xabar "
              "bo'lishi mumkin. Tez orada javob beramiz.",
        "ru": "✅ Готово! Теперь опишите проблему или задайте вопрос — текстом, фото, видео или "
              "голосовым сообщением. Мы скоро ответим.",
        "en": "✅ All set! Now describe your issue or ask a question — text, photo, video or voice "
              "message. We'll reply soon.",
    },
    "welcome_back": {
        "uz": "Assalomu alaykum! 👋 Savolingizni yozing — tez orada javob beramiz.",
        "ru": "Здравствуйте! 👋 Напишите ваш вопрос — мы скоро ответим.",
        "en": "Hello! 👋 Write your question — we'll reply soon.",
    },
    "lang_saved": {
        "uz": "✅ Til: O'zbekcha",
        "ru": "✅ Язык: Русский",
        "en": "✅ Language: English",
    },
    "received": {
        "uz": "✅ Murojaatingiz qabul qilindi. Tez orada javob beramiz.",
        "ru": "✅ Ваше обращение принято. Мы скоро ответим.",
        "en": "✅ Your request has been received. We'll reply soon.",
    },
    "banned": {
        "uz": "Kechirasiz, murojaatlaringiz qabul qilinmaydi.",
        "ru": "К сожалению, ваши обращения не принимаются.",
        "en": "Sorry, your messages are not accepted.",
    },
    "unsupported": {
        "uz": "Bu turdagi xabarni qabul qila olmaymiz. Iltimos, matn, rasm, video yoki fayl yuboring.",
        "ru": "Этот тип сообщения не поддерживается. Отправьте текст, фото, видео или файл.",
        "en": "This message type isn't supported. Please send text, a photo, video or file.",
    },
}

USER_COMMANDS = {
    "uz": [("start", "Botni boshlash"), ("lang", "Tilni o'zgartirish")],
    "ru": [("start", "Запустить бота"), ("lang", "Сменить язык")],
    "en": [("start", "Start the bot"), ("lang", "Change language")],
}

SKIP_TEXTS = set(TEXTS["skip"].values())


def t(key: str, lang: str | None) -> str:
    return TEXTS[key].get(lang or "uz") or TEXTS[key]["uz"]