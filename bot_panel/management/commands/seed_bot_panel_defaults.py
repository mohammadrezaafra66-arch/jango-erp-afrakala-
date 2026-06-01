from __future__ import annotations

from django.core.management.base import BaseCommand

from bot_panel.models import BotAgent, BotCommandTemplate


DEFAULT_BOTS = [
    {
        "slug": "market-data-bot",
        "name": "ربات نرخ دلار تهران",
        "description": "جمع‌آوری نرخ‌ها و شاخص‌های بازار از dollar-tehran-bot.",
        "commands": [
            {
                "code": "collect-rates",
                "title": "جمع‌آوری نرخ‌ها",
                "description": "اجرای ربات نرخ‌ها. برای تست امن dry_run=true و برای اجرای واقعی bot_path را در input_payload قرار دهید.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "dry_run": {"type": "boolean", "default": True},
                        "bot_path": {"type": "string"},
                        "market_data_bot_path": {"type": "string"},
                        "config_path": {"type": "string"},
                        "include_snapshots": {"type": "boolean", "default": False},
                    },
                    "required": [],
                },
            }
        ],
    },
    {
        "slug": "price-update-bot",
        "name": "ربات بروزرسانی قیمت",
        "description": "نمونه آزمایشی برای اعتبارسنجی مسیر اجرای بات‌ها. فعلاً قیمت واقعی را تغییر نمی‌دهد.",
        "commands": [
            {
                "code": "update-price",
                "title": "بروزرسانی آزمایشی قیمت",
                "description": "اجرای نمونه آزمایشی بدون تغییر واقعی قیمت‌ها.",
                "input_schema": {"type": "object", "properties": {}, "required": []},
            }
        ],
    },
]


class Command(BaseCommand):
    help = "Create or update default BotAgent and BotCommandTemplate records for bot_panel."

    def add_arguments(self, parser):
        parser.add_argument(
            "--deactivate-missing",
            action="store_true",
            help="Deactivate existing BotAgent/BotCommandTemplate records that are not in the default list.",
        )

    def handle(self, *args, **options):
        deactivate_missing = options["deactivate_missing"]
        known_bot_slugs = set()
        known_command_keys = set()
        created_bots = 0
        updated_bots = 0
        created_commands = 0
        updated_commands = 0

        for bot_data in DEFAULT_BOTS:
            known_bot_slugs.add(bot_data["slug"])
            bot, created = BotAgent.objects.update_or_create(
                slug=bot_data["slug"],
                defaults={
                    "name": bot_data["name"],
                    "description": bot_data["description"],
                    "is_active": True,
                },
            )
            if created:
                created_bots += 1
            else:
                updated_bots += 1

            for command_data in bot_data["commands"]:
                known_command_keys.add((bot.slug, command_data["code"]))
                _, command_created = BotCommandTemplate.objects.update_or_create(
                    bot=bot,
                    code=command_data["code"],
                    defaults={
                        "title": command_data["title"],
                        "description": command_data["description"],
                        "input_schema": command_data["input_schema"],
                        "is_active": True,
                    },
                )
                if command_created:
                    created_commands += 1
                else:
                    updated_commands += 1

        deactivated_bots = 0
        deactivated_commands = 0
        if deactivate_missing:
            deactivated_bots = BotAgent.objects.exclude(slug__in=known_bot_slugs).update(is_active=False)
            for command in BotCommandTemplate.objects.select_related("bot").all():
                if (command.bot.slug, command.code) not in known_command_keys and command.is_active:
                    command.is_active = False
                    command.save(update_fields=["is_active", "updated_at"])
                    deactivated_commands += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Bot panel defaults synced. "
                f"bots created={created_bots}, bots updated={updated_bots}, "
                f"commands created={created_commands}, commands updated={updated_commands}, "
                f"bots deactivated={deactivated_bots}, commands deactivated={deactivated_commands}"
            )
        )
