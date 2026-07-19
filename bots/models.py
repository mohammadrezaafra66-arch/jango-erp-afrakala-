from django.db import models

from core.models import TimeStampedModel


class BotApiKey(TimeStampedModel):
    name = models.CharField(max_length=120, unique=True)
    key_hash = models.CharField(max_length=128)
    scopes = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name


class BotRequestLog(TimeStampedModel):
    bot_key = models.ForeignKey(BotApiKey, on_delete=models.SET_NULL, null=True, blank=True)
    path = models.CharField(max_length=240)
    method = models.CharField(max_length=12)
    status_code = models.PositiveIntegerField()
    remote_addr = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.method} {self.path} {self.status_code}"
