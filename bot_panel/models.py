from django.conf import settings
from django.db import models


class BotAgent(models.Model):
    name = models.CharField("نام بات", max_length=120)
    slug = models.SlugField("شناسه یکتا", max_length=120, unique=True)
    description = models.TextField("توضیح ساده", blank=True)
    is_active = models.BooleanField("فعال است؟", default=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "بات"
        verbose_name_plural = "بات‌ها"
        ordering = ["name"]

    def __str__(self):
        return self.name


class BotCommandTemplate(models.Model):
    bot = models.ForeignKey(BotAgent, related_name="command_templates", on_delete=models.CASCADE, verbose_name="بات")
    title = models.CharField("عنوان عملیات", max_length=150)
    code = models.SlugField("کد عملیات", max_length=120)
    description = models.TextField("توضیح ساده", blank=True)
    input_schema = models.JSONField("ساختار ورودی", default=dict, blank=True)
    is_active = models.BooleanField("فعال است؟", default=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "عملیات بات"
        verbose_name_plural = "عملیات‌های بات"
        ordering = ["bot__name", "title"]
        unique_together = [["bot", "code"]]

    def __str__(self):
        return f"{self.bot.name} - {self.title}"


class BotRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "در انتظار اجرا"),
        ("running", "در حال اجرا"),
        ("success", "موفق"),
        ("failed", "ناموفق"),
        ("needs_review", "نیازمند بررسی مدیر"),
        ("cancelled", "لغو شده"),
    ]

    requested_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="controlled_bot_requests", on_delete=models.PROTECT, verbose_name="ثبت‌کننده")
    bot = models.ForeignKey(BotAgent, related_name="requests", on_delete=models.PROTECT, verbose_name="بات")
    command_template = models.ForeignKey(BotCommandTemplate, related_name="requests", on_delete=models.PROTECT, verbose_name="نوع عملیات")
    title = models.CharField("عنوان درخواست", max_length=180)
    user_message = models.TextField("توضیح درخواست", blank=True)
    input_payload = models.JSONField("داده‌های ورودی", default=dict, blank=True)
    status = models.CharField("وضعیت", max_length=30, choices=STATUS_CHOICES, default="pending", db_index=True)
    user_friendly_status = models.CharField("پیام ساده برای کاربر", max_length=255, blank=True, default="درخواست ثبت شد و در صف بررسی قرار گرفت.")
    result_summary = models.TextField("خلاصه نتیجه", blank=True)
    error_message_for_user = models.TextField("خطای قابل نمایش به کاربر", blank=True)
    technical_error = models.TextField("خطای فنی", blank=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)
    started_at = models.DateTimeField("زمان شروع", null=True, blank=True)
    finished_at = models.DateTimeField("زمان پایان", null=True, blank=True)

    class Meta:
        verbose_name = "درخواست بات"
        verbose_name_plural = "درخواست‌های بات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} - {self.title}"


class BotRunLog(models.Model):
    LEVEL_CHOICES = [
        ("info", "اطلاع‌رسانی"),
        ("warning", "هشدار"),
        ("error", "خطا"),
        ("debug", "فنی"),
    ]

    bot_request = models.ForeignKey(BotRequest, related_name="logs", on_delete=models.CASCADE, verbose_name="درخواست بات")
    level = models.CharField("سطح گزارش", max_length=20, choices=LEVEL_CHOICES, default="info")
    message = models.TextField("پیام قابل مشاهده")
    technical_message = models.TextField("پیام فنی", blank=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)

    class Meta:
        verbose_name = "گزارش اجرای بات"
        verbose_name_plural = "گزارش‌های اجرای بات"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_level_display()} - request #{self.bot_request_id}"
