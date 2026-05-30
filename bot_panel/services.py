from .models import BotRunLog


def run_bot_request(bot_request):
    """Placeholder for future real bot/API execution."""
    BotRunLog.objects.create(
        bot_request=bot_request,
        level="info",
        message="درخواست شما با موفقیت ثبت شد و در صف بررسی ربات قرار گرفت.",
        technical_message="MVP placeholder: external bot runner is not configured yet.",
    )
    return bot_request
