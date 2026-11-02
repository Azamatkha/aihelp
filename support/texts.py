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
    "welcome": {
        "uz": "✅ Ro'yxatdan o'tdingiz, {name}! Rahmat.\n\n"
              "Bu bot orqali:\n"
              "💬 Savol yoki muammongizni yozing — matn, rasm, video yoki ovozli xabar bo'lishi mumkin, "
              "mutaxassislarimiz tez orada javob berishadi.\n"
              "📲 Turon AI ilovasini yuklab olish uchun pastdagi «Ilovani yuklab olish» tugmasini bosing.",
        "ru": "✅ Вы зарегистрированы, {name}! Спасибо.\n\n"
              "С помощью этого бота вы можете:\n"
              "💬 Задать вопрос или описать проблему — текстом, фото, видео или голосовым сообщением, "
              "наши специалисты скоро ответят.\n"
              "📲 Скачать приложение Turon AI — нажмите кнопку «Скачать приложение» ниже.",
        "en": "✅ You're registered, {name}! Thank you.\n\n"
              "With this bot you can:\n"
              "💬 Ask a question or describe an issue — text, photo, video or voice message, "
              "our specialists will reply soon.\n"
              "📲 Download the Turon AI app — tap the «Download the app» button below.",
    },
    "welcome_back": {
        "uz": "Assalomu alaykum, {name}! 👋 Sizni yana ko'rganimizdan xursandmiz.\n\n"
              "💬 Savolingizni yozing — tez orada javob beramiz.\n"
              "📲 Ilova kerak bo'lsa — pastdagi tugmani bosing.",
        "ru": "Здравствуйте, {name}! 👋 Рады видеть вас снова.\n\n"
              "💬 Напишите ваш вопрос — мы скоро ответим.\n"
              "📲 Нужно приложение — нажмите кнопку ниже.",
        "en": "Hello, {name}! 👋 Good to see you again.\n\n"
              "💬 Write your question — we'll reply soon.\n"
              "📲 Need the app? Tap the button below.",
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
    "apk_caption": {
        "uz": "📲 Turon AI — Android ilovasi",
        "ru": "📲 Turon AI — приложение для Android",
        "en": "📲 Turon AI — Android app",
    },
    "apk_guide": {
        "uz": "⚠️ <b>Ilova faqat Android telefonlar uchun.</b> iPhone (iOS) ga o'rnatib bo'lmaydi.\n\n"
              "<b>Qanday o'rnatiladi:</b>\n"
              "1️⃣ Yuqoridagi faylni bosing — telefoningizga yuklab olinadi.\n"
              "2️⃣ Yuklab bo'lingach, faylni yana bosing va <b>«O'rnatish»</b> ni tanlang.\n"
              "3️⃣ <i>«Noma'lum manbadan o'rnatish»</i> haqida ogohlantirish chiqsa: "
              "<b>Sozlamalar</b> → <b>«Shu manbadan ruxsat berish»</b> ni yoqing va orqaga qayting.\n"
              "4️⃣ Google Play Protect ogohlantirsa: <b>«Batafsil»</b> → <b>«Baribir o'rnatish»</b>.\n"
              "5️⃣ O'rnatilgach, ilova menyuda paydo bo'ladi — oching va foydalaning.\n\n"
              "Muammo bo'lsa — shu yerga yozing, yordam beramiz.",
        "ru": "⚠️ <b>Приложение только для Android-телефонов.</b> На iPhone (iOS) установить нельзя.\n\n"
              "<b>Как установить:</b>\n"
              "1️⃣ Нажмите на файл выше — он скачается на телефон.\n"
              "2️⃣ После загрузки нажмите на файл ещё раз и выберите <b>«Установить»</b>.\n"
              "3️⃣ Если появится предупреждение <i>«Установка из неизвестных источников»</i>: "
              "<b>Настройки</b> → включите <b>«Разрешить из этого источника»</b> и вернитесь назад.\n"
              "4️⃣ Если предупреждает Google Play Protect: <b>«Подробнее»</b> → <b>«Всё равно установить»</b>.\n"
              "5️⃣ После установки приложение появится в меню — откройте его и пользуйтесь.\n\n"
              "Если возникнут проблемы — напишите сюда, мы поможем.",
        "en": "⚠️ <b>The app is for Android phones only.</b> It can't be installed on iPhone (iOS).\n\n"
              "<b>How to install:</b>\n"
              "1️⃣ Tap the file above — it will download to your phone.\n"
              "2️⃣ When it's downloaded, tap the file again and choose <b>«Install»</b>.\n"
              "3️⃣ If you see an <i>«Install unknown apps»</i> warning: "
              "<b>Settings</b> → turn on <b>«Allow from this source»</b> and go back.\n"
              "4️⃣ If Google Play Protect warns you: <b>«More details»</b> → <b>«Install anyway»</b>.\n"
              "5️⃣ Once installed, the app appears in your app list — open it and you're ready.\n\n"
              "If something goes wrong — write here and we'll help.",
    },
    "apk_missing": {
        "uz": "😔 Ilova fayli hozircha mavjud emas. Birozdan so'ng qayta urinib ko'ring.",
        "ru": "😔 Файл приложения пока недоступен. Попробуйте чуть позже.",
        "en": "😔 The app file isn't available yet. Please try again a bit later.",
    },
}

USER_COMMANDS = {
    "uz": [("start", "Botni boshlash"), ("app", "Ilovani yuklab olish (Android)"), ("lang", "Tilni o'zgartirish")],
    "ru": [("start", "Запустить бота"), ("app", "Скачать приложение (Android)"), ("lang", "Сменить язык")],
    "en": [("start", "Start the bot"), ("app", "Download the app (Android)"), ("lang", "Change language")],
}

SKIP_TEXTS = set(TEXTS["skip"].values())
GET_APP_TEXTS = set(TEXTS["get_app"].values())


def t(key: str, lang: str | None, **kw) -> str:
    text = TEXTS[key].get(lang or "uz") or TEXTS[key]["uz"]
    return text.format(**kw) if kw else text
