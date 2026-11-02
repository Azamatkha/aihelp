from django.db import models


class TelegramUser(models.Model):
    class Lang(models.TextChoices):
        UZ = "uz", "O'zbekcha"
        RU = "ru", "Русский"
        EN = "en", "English"

    class Step(models.TextChoices):
        LANG = "lang", "Til tanlamoqda"
        PHONE = "phone", "Telefon kutilmoqda"
        DONE = "done", "Ro'yxatdan o'tgan"

    telegram_id = models.BigIntegerField("Telegram ID", unique=True)
    username = models.CharField("Username", max_length=64, blank=True)
    full_name = models.CharField("Ism", max_length=256, blank=True)
    language = models.CharField("Til", max_length=2, choices=Lang.choices, blank=True)
    phone = models.CharField("Telefon", max_length=32, blank=True)
    reg_step = models.CharField("Ro'yxat bosqichi", max_length=8, choices=Step.choices, default=Step.LANG)
    is_banned = models.BooleanField("Bloklangan", default=False)
    created_at = models.DateTimeField("Birinchi kirgan", auto_now_add=True)
    last_message_at = models.DateTimeField("Oxirgi murojaat", null=True, blank=True)

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"
        ordering = ["-last_message_at", "-created_at"]

    def __str__(self) -> str:
        name = self.full_name or str(self.telegram_id)
        return f"{name} (@{self.username})" if self.username else name


class Message(models.Model):
    class Direction(models.TextChoices):
        IN = "in", "Userdan"
        OUT = "out", "Admin javobi"

    class Status(models.TextChoices):
        NEW = "new", "Javob kutilmoqda"
        ANSWERED = "answered", "Javob berilgan"
        CLOSED = "closed", "Yopilgan"
        SENT = "sent", "Yuborildi"
        FAILED = "failed", "Yetkazilmadi"

    user = models.ForeignKey(
        TelegramUser, on_delete=models.CASCADE, related_name="messages", verbose_name="Foydalanuvchi"
    )
    direction = models.CharField("Yo'nalish", max_length=3, choices=Direction.choices)
    status = models.CharField("Holat", max_length=10, choices=Status.choices)
    # text, photo, video, voice, document, album ...
    content_type = models.CharField("Turi", max_length=20, default="text")
    items = models.PositiveSmallIntegerField("Fayllar soni", default=1)
    text = models.TextField("Matn", blank=True)
    # Userning chatidagi xabar ID — javob aynan shu xabarga reply bo'lib boradi
    user_msg_id = models.BigIntegerField(null=True, blank=True)
    admin_name = models.CharField("Admin", max_length=128, blank=True)
    created_at = models.DateTimeField("Vaqt", auto_now_add=True, db_index=True)
    answered_at = models.DateTimeField("Javob vaqti", null=True, blank=True)

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"#{self.pk} {self.text[:50] or self.content_type}"


class AdminCard(models.Model):
    """Adminga yuborilgan Telegram xabari. Admin unga Reply qilsa,
    qaysi murojaatga javob ekanini shu jadvaldan topamiz."""

    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name="cards")
    admin_chat_id = models.BigIntegerField()
    card_msg_id = models.BigIntegerField()
    # False — bu karta emas, user yuborgan media nusxasi (tahrirlanmaydi)
    is_card = models.BooleanField(default=True)

    class Meta:
        unique_together = [("admin_chat_id", "card_msg_id")]


class AdminState(models.Model):
    """Admin '✍️ Javob yozish' ni bosgandan keyin kimga yozayotgani."""

    admin_id = models.BigIntegerField(unique=True)
    reply_to = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True)