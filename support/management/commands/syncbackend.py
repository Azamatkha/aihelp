from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from support import sync


class Command(BaseCommand):
    help = "Bot ma'lumotlarini turon-ai backendga bir marta yuboradi (tekshirish uchun)"

    def add_arguments(self, parser):
        parser.add_argument("--full", action="store_true",
                            help="Barcha xabarlarni qaytadan yuborish (faqat o'zgarganlarini emas)")

    def handle(self, *args, **options):
        if not sync.enabled():
            raise CommandError(".env da BACKEND_URL yoki BACKEND_API_KEY yo'q")
        self.stdout.write(f"Manzil: {settings.BACKEND_URL}  |  proxy: {settings.BACKEND_PROXY or 'yo`q'}")
        try:
            users, messages = sync.sync_once(full=options["full"])
        except Exception as e:
            raise CommandError(f"Yuborib bo'lmadi: {type(e).__name__}: {e}") from e
        self.stdout.write(self.style.SUCCESS(f"Yuborildi: {users} user, {messages} xabar"))
