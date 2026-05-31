from __future__ import annotations


def run(input_payload: dict, user_message: str, context: dict | None = None) -> dict:
    """Safe sample worker for validating the bot_panel runner path."""
    return {
        "summary": "اجرای آزمایشی بات بروزرسانی قیمت با موفقیت انجام شد.",
        "data": {
            "input_payload": input_payload,
            "user_message": user_message,
            "context": context or {},
            "mode": "sample",
        },
    }
