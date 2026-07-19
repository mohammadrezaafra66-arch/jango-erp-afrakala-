from django.core.management.base import BaseCommand

from bot_panel.models import BotRequest
from bot_panel.services import run_bot_request


class Command(BaseCommand):
    help = "Run pending bot requests."

    def add_arguments(self, parser):
        parser.add_argument("--request-id", type=int, default=None)
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **options):
        request_id = options.get("request_id")
        limit = options.get("limit")

        queryset = (
            BotRequest.objects.select_related(
                "bot",
                "command_template",
                "requested_by",
            )
            .filter(status="pending")
            .order_by("created_at", "id")
        )

        if request_id is not None:
            queryset = queryset.filter(pk=request_id)

        if limit is not None:
            queryset = queryset[:max(0, limit)]

        bot_requests = list(queryset)

        success = 0
        failed = 0
        needs_review = 0
        other = 0

        self.stdout.write(f"Found {len(bot_requests)} pending bot request(s).")

        for bot_request in bot_requests:
            self.stdout.write(f"Running BotRequest #{bot_request.pk}: {bot_request.title}")

            result = run_bot_request(bot_request)

            if result.status == "success":
                success += 1
            elif result.status == "failed":
                failed += 1
            elif result.status == "needs_review":
                needs_review += 1
            else:
                other += 1

            self.stdout.write(f"  -> {result.status}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. total={len(bot_requests)}, "
                f"success={success}, "
                f"failed={failed}, "
                f"needs_review={needs_review}, "
                f"other={other}"
            )
        )
