from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Any

BotHandler = Callable[[dict, str, dict | None], dict]

# Registry rule:
#   key   = (bot.slug, command_template.code)
#   value = callable handler or dotted import path
#
# Dotted import paths are intentional: a broken optional bot dependency must not
# crash Django startup/admin. Import happens only when the runner needs it.
BOT_COMMAND_HANDLERS: dict[tuple[str, str], BotHandler | str] = {
    ("market-data-bot", "collect-rates"): "bot_workers.market_data_collect.run",
    ("price-update-bot", "update-price"): "bot_workers.sample_price_update.run",
}


def _import_from_dotted_path(dotted_path: str) -> BotHandler:
    module_path, _, attr_name = dotted_path.rpartition(".")
    if not module_path or not attr_name:
        raise ImportError(f"Invalid handler path: {dotted_path}")

    module = import_module(module_path)
    handler = getattr(module, attr_name)

    if not callable(handler):
        raise TypeError(f"Bot handler is not callable: {dotted_path}")

    return handler


def get_bot_handler(bot_slug: str, command_code: str) -> BotHandler | None:
    handler: BotHandler | str | None = BOT_COMMAND_HANDLERS.get((bot_slug, command_code))

    if handler is None:
        return None

    if isinstance(handler, str):
        return _import_from_dotted_path(handler)

    if not callable(handler):
        raise TypeError(f"Invalid bot handler for ({bot_slug}, {command_code})")

    return handler


def list_registered_handlers() -> list[dict[str, Any]]:
    return [
        {"bot_slug": bot_slug, "command_code": command_code, "handler": str(handler)}
        for (bot_slug, command_code), handler in sorted(BOT_COMMAND_HANDLERS.items())
    ]
