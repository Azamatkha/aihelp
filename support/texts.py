"""Foydalanuvchiga ko'rinadigan matnlar. Admin tomoni — o'zbekcha, bot.py da."""

FLAGS = {"uz": "🇺🇿", "ru": "🇷🇺", "en": "🇬🇧"}
LANG_BUTTONS = [("uz", "🇺🇿 O'zbekcha"), ("ru", "🇷🇺 Русский"), ("en", "🇬🇧 English")]

CHOOSE_LANG = (
    "👋 Assalomu alaykum! Turon AI yordam botiga xush kelibsiz.\n"
    "👋 Здравствуйте! Добро пожаловать в бот поддержки Turon AI.\n"
    "👋 Hello! Welcome to the Turon AI support bot.\n\n"
    "🇺🇿 Tilni tanlang\n🇷🇺 Выберите язык\n🇬🇧 Choose your language"
)

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
    "registered": {
        "uz": "✅ Ro'yxatdan o'tdingiz, rahmat!",
        "ru": "✅ Вы зарегистрированы, спасибо!",
        "en": "✅ You're registered, thank you!",
    },
    "greeting": {
        "uz": "Assalomu alaykum, {name}! 👋\n\n"
              "💬 Savol yoki muammo bo'lsa — shu yerga yozing (matn, rasm, video yoki ovozli xabar), "
              "tez orada javob beramiz.\n\n"
              "📲 Verifikatsiyadan o'tish uchun pastdagi tugma orqali ilovani yuklab oling.",
        "ru": "Здравствуйте, {name}! 👋\n\n"
              "💬 Если есть вопрос или проблема — напишите сюда (текст, фото, видео или голосовое), "
              "мы скоро ответим.\n\n"
              "📲 Для прохождения верификации скачайте приложение по кнопке ниже.",
        "en": "Hello, {name}! 👋\n\n"
              "💬 If you have a question or an issue — write here (text, photo, video or voice), "
              "we'll reply soon.\n\n"
              "📲 To pass verification, download the app using the button below.",
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
    "get_app": {"uz": "📲 Ilovani yuklab olish", "ru": "📲 Скачать приложение", "en": "📲 Download the app"},
    # Fayl tagidagi yozuv (caption, 1024 belgidan oshmasin)
    "apk_caption": {
        "uz": "📲 <b>Turon AI ilovasi</b>\n\n"
              "⚠️ Faqat <b>Android</b> telefonlarga (Samsung, Xiaomi, Redmi, Honor, Tecno ...) "
              "yuklab olishingiz mumkin. iPhone'ga o'rnatilmaydi.\n\n"
              "Faylni bosing → «O'rnatish». Ochilmasa, boshqa Android telefonda sinab ko'ring.",
        "ru": "📲 <b>Приложение Turon AI</b>\n\n"
              "⚠️ Можно установить только на телефоны <b>Android</b> (Samsung, Xiaomi, Redmi, Honor, Tecno ...). "
              "На iPhone не устанавливается.\n\n"
              "Нажмите на файл → «Установить». Если не открывается, попробуйте на другом Android-телефоне.",
        "en": "📲 <b>Turon AI app</b>\n\n"
              "⚠️ Can be installed on <b>Android</b> phones only (Samsung, Xiaomi, Redmi, Honor, Tecno ...). "
              "It won't install on iPhone.\n\n"
              "Tap the file → «Install». If it doesn't open, try another Android phone.",
    },
    "apk_missing": {
        "uz": "😔 Ilova fayli hozircha mavjud emas. Birozdan so'ng qayta urinib ko'ring.",
        "ru": "😔 Файл приложения пока недоступен. Попробуйте чуть позже.",
        "en": "😔 The app file isn't available yet. Please try again a bit later.",
    },
}

# Menyu buyruqlari — user tanlagan tilda ko'rsatiladi (bot.set_user_commands)
USER_COMMANDS = {
    "uz": [("start", "Botni boshlash"), ("yuklash", "Ilovani yuklab olish (faqat Android)"),
           ("lang", "Tilni o'zgartirish")],
    "ru": [("start", "Запустить бота"), ("yuklash", "Скачать приложение (только Android)"),
           ("lang", "Сменить язык")],
    "en": [("start", "Start the bot"), ("yuklash", "Download the app (Android only)"),
           ("lang", "Change language")],
}

SKIP_TEXTS = set(TEXTS["skip"].values())
GET_APP_TEXTS = set(TEXTS["get_app"].values())


def t(key: str, lang: str | None, **kw) -> str:
    text = TEXTS[key].get(lang or "uz") or TEXTS[key]["uz"]
    return text.format(**kw) if kw else text
