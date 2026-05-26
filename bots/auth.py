import hashlib
from dataclasses import dataclass

from django.http import HttpRequest

from .models import BotApiKey

BOT_KEY_HEADER = "HTTP_X_BOT_API_KEY"


@dataclass
class BotAuthResult:
    status_code: int
    bot_key: BotApiKey | None = None
    error: str | None = None


def hash_bot_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def authenticate_bot_request(request: HttpRequest, required_scope: str) -> BotAuthResult:
    raw_key = request.META.get(BOT_KEY_HEADER, "").strip()
    if not raw_key:
        return BotAuthResult(status_code=401, error="missing_bot_api_key")

    key_hash = hash_bot_key(raw_key)
    bot_key = BotApiKey.objects.filter(key_hash=key_hash).first()
    if bot_key is None:
        return BotAuthResult(status_code=401, error="invalid_bot_api_key")

    if not bot_key.is_active:
        return BotAuthResult(status_code=403, bot_key=bot_key, error="disabled_bot_api_key")

    scopes = bot_key.scopes or []
    if required_scope not in scopes:
        return BotAuthResult(status_code=403, bot_key=bot_key, error="missing_scope")

    return BotAuthResult(status_code=200, bot_key=bot_key)
