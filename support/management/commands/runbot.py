from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from support.bot import get_bot, setup_commands
from support.sync import start_sync_thread


class Command(BaseCommand):
    help = "Botni ishga tushiradi (long polling)"

    def handle(self, *args, **options):
        if not settings.BOT_TOKEN:
            raise CommandError(".env da BOT_TOKEN yo'q")
        if not settings.ADMIN_IDS:
            raise CommandError(".env da ADMIN_IDS yo'q")

        bot = get_bot()
        bot.remove_webhook()
        setup_commands(bot)
        me = bot.get_me()
        self.stdout.write(self.style.SUCCESS(f"@{me.username} ishga tushdi. To'xtatish: Ctrl+C"))
        # Userlar va murojaatlar turon-ai backendga fonda yuborib turiladi
        start_sync_thread()
        # skip_pending=False — kompyuter o'chiq paytda kelgan xabarlar ham qayta ishlanadi
        bot.infinity_polling(skip_pending=False, timeout=30, long_polling_timeout=25)