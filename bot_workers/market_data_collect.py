from __future__ import annotations

from pathlib import Path
from typing import Any


def _find_market_data_config(input_payload: dict) -> str:
    config_path = input_payload.get("config_path") or input_payload.get("config")
    if config_path:
        return str(config_path)

    candidates = [
        Path("configs") / "indicators.json",
        Path("../dollar-tehran-bot/configs/indicators.json"),
        Path("dollar-tehran-bot/configs/indicators.json"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)

    return "configs/indicators.json"


def run(input_payload: dict, user_message: str, context: dict | None = None) -> dict:
    """Collect market/rate data through the existing afra_market_data bot.

    Expected bot_panel mapping:
        bot.slug = market-data-bot
        command_template.code = collect-rates

    Optional input_payload:
        dry_run: true                -> do not call external websites
        config_path: "path/to/json"  -> custom indicators config
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

    try:
        from afra_market_data.core import run_once
    except Exception as exc:
        raise RuntimeError(
            "ماژول afra_market_data در این پروژه در دسترس نیست. "
            "کد ربات نرخ‌ها را کنار پروژه Django قرار بده یا مسیر import را اصلاح کن."
        ) from exc

    config_path = _find_market_data_config(input_payload)
    payload: dict[str, Any] = run_once(config_path)
    snapshots = payload.get("snapshots", [])
    meta = payload.get("meta", {})

    return {
        "summary": f"ربات نرخ‌ها اجرا شد. تعداد شاخص‌ها: {len(snapshots)}، تعداد منابع: {meta.get('source_count', 0)}.",
        "data": {
            "config_path": config_path,
            "meta": meta,
            "snapshots_count": len(snapshots),
            "snapshots": snapshots,
        },
    }
