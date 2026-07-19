# Bot Panel Runbook

This document describes the MVP bot runner flow used by the AfraKala Django admin.

## Purpose

The `bot_panel` app lets an admin create `BotRequest` records and run them later through a management command. Bot execution is intentionally not triggered from Django Admin save hooks, because a bot can be slow, fail, or depend on external websites.

## Initial setup

Run migrations first:

```bash
python manage.py migrate
```

Create or update the default bot records:

```bash
python manage.py seed_bot_panel_defaults
```

This creates/updates:

- `market-data-bot / collect-rates`
- `price-update-bot / update-price`

## Safe dry-run test

Create a `BotRequest` in Django Admin:

- Bot: `market-data-bot`
- Command: `collect-rates`
- Status: `pending`
- Input payload:

```json
{
  "dry_run": true
}
```

Then run:

```bash
python manage.py run_pending_bot_requests
```

Expected result:

- `status = success`
- `result_summary` is filled
- at least two `BotRunLog` rows are created

## Real market-data run

The real market-data worker needs access to the cloned `dollar-tehran-bot` repository that contains `afra_market_data/`.

You can pass the path in the `BotRequest.input_payload`:

```json
{
  "dry_run": false,
  "bot_path": "C:\\Users\\AFRA\\Desktop\\dollar-tehran-bot",
  "include_snapshots": false
}
```

Or set it in local environment:

```env
AFRA_MARKET_DATA_BOT_PATH=C:\Users\AFRA\Desktop\dollar-tehran-bot
```

Optional custom config path:

```env
AFRA_MARKET_DATA_CONFIG_PATH=C:\Users\AFRA\Desktop\dollar-tehran-bot\configs\indicators.json
```

Run pending requests:

```bash
python manage.py run_pending_bot_requests
```

## Adding a new bot

Every bot handler must expose this callable contract:

```python
def run(input_payload: dict, user_message: str, context: dict | None = None) -> dict:
    return {"summary": "Done", "data": {}}
```

Add the handler path to `bot_panel/bot_registry.py`:

```python
BOT_COMMAND_HANDLERS = {
    ("new-bot-slug", "new-command-code"): "bot_workers.new_worker.run",
}
```

Then add a matching `BotAgent` and `BotCommandTemplate` record, either through Django Admin or by extending `seed_bot_panel_defaults.py`.

## Operational rules

- Do not execute bots from admin `save_model`.
- Keep `technical_error` and traceback visible only to admins.
- If a handler is missing, the request should become `needs_review`, not `failed`.
- If a handler raises an exception, only that request should become `failed`; the runner must continue with other requests.
- Do not commit local `db.sqlite3`.
