from django.contrib import admin, messages
from django.utils import timezone

from .models import BotAgent, BotCommandTemplate, BotRequest, BotRunLog
from .services import run_bot_request


@admin.register(BotAgent)
class BotAgentAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug", "description")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BotCommandTemplate)
class BotCommandTemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "bot", "code", "is_active", "created_at")
    list_filter = ("bot", "is_active")
    search_fields = ("title", "code", "description", "bot__name")
    prepopulated_fields = {"code": ("title",)}


class BotRunLogInline(admin.TabularInline):
    model = BotRunLog
    extra = 0
    readonly_fields = ("created_at",)


@admin.register(BotRequest)
class BotRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "bot",
        "command_template",
        "requested_by",
        "status",
        "created_at",
        "started_at",
        "finished_at",
    )
    list_filter = ("status", "bot", "command_template", "created_at")
    search_fields = ("title", "user_message", "requested_by__username", "bot__name")
    readonly_fields = (
        "created_at",
        "updated_at",
        "started_at",
        "finished_at",
        "result_summary",
        "error_message_for_user",
        "technical_error",
    )
    actions = ("run_selected_requests", "reset_selected_requests_to_pending")
    inlines = [BotRunLogInline]

    def save_model(self, request, obj, form, change):
        if not change and not obj.requested_by_id:
            obj.requested_by = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="اجرای درخواست‌های انتخاب‌شده")
    def run_selected_requests(self, request, queryset):
        results = {"success": 0, "failed": 0, "needs_review": 0, "skipped": 0, "other": 0}

        bot_requests = queryset.select_related("bot", "command_template", "requested_by").order_by("created_at", "id")
        for bot_request in bot_requests:
            if bot_request.status != "pending":
                results["skipped"] += 1
                continue

            updated_request = run_bot_request(bot_request)
            if updated_request.status in results:
                results[updated_request.status] += 1
            else:
                results["other"] += 1

        self.message_user(
            request,
            (
                "اجرای درخواست‌ها تمام شد. "
                f"موفق: {results['success']}، "
                f"ناموفق: {results['failed']}، "
                f"نیازمند بررسی: {results['needs_review']}، "
                f"رد شده به دلیل pending نبودن: {results['skipped']}، "
                f"سایر: {results['other']}"
            ),
            level=messages.INFO,
        )

    @admin.action(description="برگرداندن درخواست‌های انتخاب‌شده به pending برای اجرای دوباره")
    def reset_selected_requests_to_pending(self, request, queryset):
        reset_count = 0
        skipped_running = 0

        for bot_request in queryset:
            if bot_request.status == "running":
                skipped_running += 1
                continue

            bot_request.status = "pending"
            bot_request.user_friendly_status = "درخواست دوباره در صف اجرا قرار گرفت."
            bot_request.result_summary = ""
            bot_request.error_message_for_user = ""
            bot_request.technical_error = ""
            bot_request.started_at = None
            bot_request.finished_at = None
            bot_request.updated_at = timezone.now()
            bot_request.save(
                update_fields=[
                    "status",
                    "user_friendly_status",
                    "result_summary",
                    "error_message_for_user",
                    "technical_error",
                    "started_at",
                    "finished_at",
                    "updated_at",
                ]
            )
            BotRunLog.objects.create(
                bot_request=bot_request,
                level="info",
                message="درخواست از پنل ادمین دوباره به وضعیت pending برگشت.",
            )
            reset_count += 1

        self.message_user(
            request,
            f"درخواست‌های برگشته به pending: {reset_count}، رد شده به دلیل running بودن: {skipped_running}",
            level=messages.INFO,
        )


@admin.register(BotRunLog)
class BotRunLogAdmin(admin.ModelAdmin):
    list_display = ("bot_request", "level", "created_at")
    list_filter = ("level", "created_at")
    search_fields = ("message", "technical_message", "bot_request__title")
    readonly_fields = ("created_at",)
