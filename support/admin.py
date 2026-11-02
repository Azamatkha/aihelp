from django.contrib import admin
from django.db.models import Count, Q

from support.models import Message, TelegramUser

admin.site.site_header = "AI Help"
admin.site.site_title = "AI Help"
admin.site.index_title = "Boshqaruv"


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    can_delete = False
    ordering = ["-created_at"]
    fields = ["created_at", "direction", "content_type", "items", "text", "status", "admin_name"]
    readonly_fields = fields
    verbose_name_plural = "Suhbat (yangilari yuqorida)"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = [
        "__str__", "telegram_id", "phone", "language", "reg_step",
        "pending_count", "is_banned", "last_message_at",
    ]
    list_filter = ["is_banned", "language", "reg_step"]
    search_fields = ["telegram_id", "username", "full_name", "phone"]
    readonly_fields = [
        "telegram_id", "username", "full_name", "phone", "language",
        "reg_step", "created_at", "last_message_at",
    ]
    fields = readonly_fields + ["is_banned"]  # panelda faqat bloklashni o'zgartirish mumkin
    inlines = [MessageInline]

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            _pending=Count("messages", filter=Q(messages__direction="in", messages__status="new"))
        )

    @admin.display(description="Javob kutmoqda", ordering="_pending")
    def pending_count(self, obj):
        return obj._pending or "—"

    def has_add_permission(self, request):
        return False


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ["id", "user", "direction", "content_type", "short_text", "status", "admin_name", "created_at"]
    list_filter = ["status", "direction", "content_type", "created_at"]
    search_fields = ["text", "user__username", "user__full_name", "user__telegram_id", "user__phone"]
    list_select_related = ["user"]
    date_hierarchy = "created_at"

    @admin.display(description="Xabar")
    def short_text(self, obj):
        return obj.text[:80] or f"[{obj.content_type}]"

    # Tarix o'zgarmas: panel faqat ko'rish uchun, javob bot orqali yoziladi
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False