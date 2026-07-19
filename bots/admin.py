from django.contrib import admin

from .models import BotApiKey, BotRequestLog


@admin.register(BotApiKey)
class BotApiKeyAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(BotRequestLog)
class BotRequestLogAdmin(admin.ModelAdmin):
    list_display = ("method", "path", "status_code", "bot_key", "created_at")
    list_filter = ("method", "status_code")
    search_fields = ("path",)
