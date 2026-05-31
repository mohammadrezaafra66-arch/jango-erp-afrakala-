from __future__ import annotations

import traceback
from typing import Any

from django.db import transaction
from django.utils import timezone

from .bot_registry import get_bot_handler
from .models import BotRequest, BotRunLog


STATUS_PENDING = "pending"
STATUS_RUNNING = "running"
STATUS_SUCCESS = "success"
STATUS_FAILED = "failed"
STATUS_NEEDS_REVIEW = "needs_review"


def _log(bot_request: BotRequest, level: str, message: str, technical_message: str = "") -> BotRunLog:
    return BotRunLog.objects.create(
        bot_request=bot_request,
        level=level,
        message=message,
        technical_message=technical_message,
    )


def _safe_payload(payload: Any) -> dict:
    return payload if isinstance(payload, dict) else {}


def _mark_needs_review(bot_request: BotRequest, user_message: str, technical_message: str) -> BotRequest:
    bot_request.status = STATUS_NEEDS_REVIEW
    bot_request.user_friendly_status = user_message
    bot_request.technical_error = technical_message
    bot_request.finished_at = timezone.now()
    bot_request.save(
        update_fields=[
            "status",
            "user_friendly_status",
            "technical_error",
            "finished_at",
            "updated_at",
        ]
    )
    _log(bot_request, "warning", user_message, technical_message)
    return bot_request


def run_bot_request(bot_request: BotRequest) -> BotRequest:
    """Run one pending BotRequest safely.

    This function is intentionally synchronous and command-runner friendly.
    It must never be called from admin save hooks because bot execution can be
    slow, fail, or depend on optional external services.
    """

    with transaction.atomic():
        locked_request = (
            BotRequest.objects.select_for_update()
            .select_related("bot", "command_template", "requested_by")
            .get(pk=bot_request.pk)
        )

        if locked_request.status != STATUS_PENDING:
            _log(
                locked_request,
                "debug",
                "درخواست اجرا نشد چون وضعیت آن pending نبود.",
                f"Current status: {locked_request.status}",
            )
            return locked_request

        if not locked_request.bot.is_active:
            return _mark_needs_review(
                locked_request,
                "این بات غیرفعال است و فعلاً قابل اجرا نیست.",
                f"Inactive bot: {locked_request.bot.slug}",
            )

        if not locked_request.command_template.is_active:
            return _mark_needs_review(
                locked_request,
                "این عملیات بات غیرفعال است و فعلاً قابل اجرا نیست.",
                f"Inactive command: {locked_request.bot.slug}/{locked_request.command_template.code}",
            )

        locked_request.status = STATUS_RUNNING
        locked_request.user_friendly_status = "درخواست در حال اجرا است."
        locked_request.started_at = timezone.now()
        locked_request.error_message_for_user = ""
        locked_request.technical_error = ""
        locked_request.save(
            update_fields=[
                "status",
                "user_friendly_status",
                "started_at",
                "error_message_for_user",
                "technical_error",
                "updated_at",
            ]
        )
        _log(
            locked_request,
            "info",
            "اجرای درخواست بات شروع شد.",
            f"bot={locked_request.bot.slug}, command={locked_request.command_template.code}",
        )

    # Keep external/slow bot execution outside the DB lock.
    bot_request = (
        BotRequest.objects.select_related("bot", "command_template", "requested_by")
        .get(pk=bot_request.pk)
    )

    try:
        handler = get_bot_handler(bot_request.bot.slug, bot_request.command_template.code)
    except Exception:
        technical = traceback.format_exc()
        bot_request.status = STATUS_NEEDS_REVIEW
        bot_request.user_friendly_status = "اجرای این بات هنوز درست پیکربندی نشده است."
        bot_request.technical_error = technical
        bot_request.finished_at = timezone.now()
        bot_request.save(
            update_fields=[
                "status",
                "user_friendly_status",
                "technical_error",
                "finished_at",
                "updated_at",
            ]
        )
        _log(bot_request, "warning", bot_request.user_friendly_status, technical)
        return bot_request

    if handler is None:
        technical = (
            "No handler registered for "
            f"bot.slug={bot_request.bot.slug!r}, "
            f"command_template.code={bot_request.command_template.code!r}"
        )
        bot_request.status = STATUS_NEEDS_REVIEW
        bot_request.user_friendly_status = "برای این درخواست هنوز اجراکننده تعریف نشده است."
        bot_request.technical_error = technical
        bot_request.finished_at = timezone.now()
        bot_request.save(
            update_fields=[
                "status",
                "user_friendly_status",
                "technical_error",
                "finished_at",
                "updated_at",
            ]
        )
        _log(bot_request, "warning", bot_request.user_friendly_status, technical)
        return bot_request

    try:
        context = {
            "bot_request_id": bot_request.pk,
            "bot_slug": bot_request.bot.slug,
            "command_code": bot_request.command_template.code,
            "requested_by_id": bot_request.requested_by_id,
            "requested_by_username": getattr(bot_request.requested_by, "username", ""),
        }
        result = handler(_safe_payload(bot_request.input_payload), bot_request.user_message, context)
        if not isinstance(result, dict):
            raise TypeError("Bot handler must return a dict.")

        bot_request.status = STATUS_SUCCESS
        bot_request.result_summary = str(result.get("summary") or "عملیات با موفقیت انجام شد.")
        bot_request.user_friendly_status = "درخواست با موفقیت انجام شد."
        bot_request.error_message_for_user = ""
        bot_request.technical_error = ""
        bot_request.finished_at = timezone.now()
        bot_request.save(
            update_fields=[
                "status",
                "result_summary",
                "user_friendly_status",
                "error_message_for_user",
                "technical_error",
                "finished_at",
                "updated_at",
            ]
        )
        _log(bot_request, "info", "اجرای درخواست بات با موفقیت تمام شد.", str(result.get("data", "")))
        return bot_request

    except Exception:
        technical = traceback.format_exc()
        bot_request.status = STATUS_FAILED
        bot_request.error_message_for_user = "در اجرای درخواست مشکلی پیش آمد. لطفاً به مسئول فنی اطلاع دهید."
        bot_request.user_friendly_status = "اجرای درخواست ناموفق بود."
        bot_request.technical_error = technical
        bot_request.finished_at = timezone.now()
        bot_request.save(
            update_fields=[
                "status",
                "error_message_for_user",
                "user_friendly_status",
                "technical_error",
                "finished_at",
                "updated_at",
            ]
        )
        _log(bot_request, "error", bot_request.error_message_for_user, technical)
        return bot_request
