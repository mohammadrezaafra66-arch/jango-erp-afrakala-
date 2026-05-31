from django.contrib import admin

from .models import BotAgent, BotCommandTemplate, BotRequest, BotRunLog


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
    list_display = ("id", "title", "bot", "command_template", "requested_by", "status", "created_at")
    list_filter = ("status", "bot", "command_template", "created_at")
    search_fields = ("title", "user_message", "requested_by__username", "bot__name")
    readonly_fields = ("created_at", "updated_at", "started_at", "finished_at")
    inlines = [BotRunLogInline]

    def save_model(self, request, obj, form, change):
        if not change and not obj.requested_by_id:
            obj.requested_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(BotRunLog)
class BotRunLogAdmin(admin.ModelAdmin):
    list_display = ("bot_request", "level", "created_at")
    list_filter = ("level", "created_at")
    search_fields = ("message", "technical_message", "bot_request__title")
    readonly_fields = ("created_at",)
