from __future__ import annotations

import os
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _as_path(value: str | None) -> Path | None:
    if not value:
        return None
    return Path(value).expanduser().resolve()


def _candidate_bot_paths(input_payload: dict) -> list[Path]:
    explicit_paths = [
        _as_path(input_payload.get("bot_path")),
        _as_path(input_payload.get("market_data_bot_path")),
        _as_path(os.getenv("AFRA_MARKET_DATA_BOT_PATH")),
    ]

    fallback_paths = [
        PROJECT_ROOT / "dollar-tehran-bot",
        PROJECT_ROOT.parent / "dollar-tehran-bot",
        PROJECT_ROOT.parent / "dollar-tehran-bot" / "dollar-tehran-bot",
        Path.home() / "Desktop" / "dollar-tehran-bot",
        Path.home() / "Desktop" / "bots" / "dollar" / "dollar-tehran-bot-git",
    ]

    return [path for path in explicit_paths + fallback_paths if path is not None]


@contextmanager
def _working_directory(path: Path) -> Iterator[None]:
    previous = Path.cwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(previous)


def _add_market_data_bot_to_pythonpath(input_payload: dict) -> Path:
    for bot_path in _candidate_bot_paths(input_payload):
        package_dir = bot_path / "afra_market_data"
        if package_dir.exists() and package_dir.is_dir():
            path_text = str(bot_path)
            if path_text not in sys.path:
                sys.path.insert(0, path_text)
            return bot_path

    searched = "\n".join(str(path) for path in _candidate_bot_paths(input_payload))
    raise RuntimeError(
        "ماژول afra_market_data پیدا نشد. مسیر ریپوی dollar-tehran-bot را با "
        "AFRA_MARKET_DATA_BOT_PATH یا input_payload.bot_path مشخص کن.\n"
        f"Searched paths:\n{searched}"
    )


def _find_market_data_config(input_payload: dict, bot_path: Path | None = None) -> str:
    explicit_config = (
        input_payload.get("config_path")
        or input_payload.get("config")
        or os.getenv("AFRA_MARKET_DATA_CONFIG_PATH")
    )
    if explicit_config:
        return str(Path(explicit_config).expanduser().resolve())

    candidates = [
        bot_path / "configs" / "indicators.json" if bot_path else None,
        PROJECT_ROOT / "configs" / "indicators.json",
        PROJECT_ROOT / "dollar-tehran-bot" / "configs" / "indicators.json",
        PROJECT_ROOT.parent / "dollar-tehran-bot" / "configs" / "indicators.json",
        PROJECT_ROOT.parent / "dollar-tehran-bot" / "dollar-tehran-bot" / "configs" / "indicators.json",
        Path.home() / "Desktop" / "dollar-tehran-bot" / "configs" / "indicators.json",
        Path.home() / "Desktop" / "bots" / "dollar" / "dollar-tehran-bot-git" / "configs" / "indicators.json",
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return str(candidate.resolve())

    return str((bot_path / "configs" / "indicators.json") if bot_path else "configs/indicators.json")


def run(input_payload: dict, user_message: str, context: dict | None = None) -> dict:
    """Collect market/rate data through the existing afra_market_data bot.

    Expected bot_panel mapping:
        bot.slug = market-data-bot
        command_template.code = collect-rates

    Optional input_payload:
        dry_run: true                       -> do not call external websites
        bot_path: "path/to/dollar-bot"      -> path containing afra_market_data/
        config_path: "path/to/indicators"  -> custom indicators config
        include_snapshots: true             -> store full snapshots in result data
    """

    input_payload = input_payload or {}
    context = context or {}

    if input_payload.get("dry_run", False):
        return {
            "summary": "اجرای آزمایشی ربات نرخ‌ها با موفقیت انجام شد.",
            "data": {
                "mode": "dry_run",
                "user_message": user_message,
                "context": context,
            },
        }

    bot_path = _add_market_data_bot_to_pythonpath(input_payload)

    try:
        from afra_market_data.core import run_once
    except Exception as exc:
        raise RuntimeError(
            "مسیر dollar-tehran-bot پیدا شد اما import ماژول afra_market_data ناموفق بود. "
            "وابستگی‌های ریپوی نرخ‌ها را نصب کن یا ساختار مسیر را بررسی کن."
        ) from exc

    config_path = _find_market_data_config(input_payload, bot_path=bot_path)
    include_snapshots = bool(input_payload.get("include_snapshots", False))

    # Run from the external bot repository so relative paths inside its config
    # such as data/market_data.db and output/ resolve in the expected project.
    with _working_directory(bot_path):
        payload: dict[str, Any] = run_once(config_path)

    snapshots = payload.get("snapshots", [])
    meta = payload.get("meta", {})

    data: dict[str, Any] = {
        "mode": "real_run",
        "bot_path": str(bot_path),
        "config_path": config_path,
        "meta": meta,
        "snapshots_count": len(snapshots),
        "snapshot_preview": snapshots[:10],
    }
    if include_snapshots:
        data["snapshots"] = snapshots

    return {
        "summary": f"ربات نرخ‌ها اجرا شد. تعداد شاخص‌ها: {len(snapshots)}، تعداد منابع: {meta.get('source_count', 0)}.",
        "data": data,
    }
