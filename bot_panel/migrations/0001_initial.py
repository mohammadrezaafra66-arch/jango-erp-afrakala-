# Generated manually for bot_panel MVP

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="BotAgent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="نام ربات")),
                ("slug", models.SlugField(max_length=120, unique=True, verbose_name="شناسه یکتا")),
                ("description", models.TextField(blank=True, verbose_name="توضیح ساده")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال است؟")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")),
            ],
            options={"verbose_name": "ربات", "verbose_name_plural": "ربات‌ها", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="BotCommandTemplate",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=150, verbose_name="عنوان عملیات")),
                ("code", models.SlugField(max_length=120, verbose_name="کد عملیات")),
                ("description", models.TextField(blank=True, verbose_name="توضیح ساده")),
                ("input_schema", models.JSONField(blank=True, default=dict, verbose_name="ساختار ورودی")),
                ("is_active", models.BooleanField(default=True, verbose_name="فعال است؟")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")),
                ("bot", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="command_templates", to="bot_panel.botagent", verbose_name="ربات")),
            ],
            options={"verbose_name": "قالب دستور ربات", "verbose_name_plural": "قالب‌های دستور ربات", "ordering": ["bot__name", "title"], "unique_together": {("bot", "code")}},
        ),
        migrations.CreateModel(
            name="BotRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=180, verbose_name="عنوان درخواست")),
                ("user_message", models.TextField(blank=True, verbose_name="توضیح کاربر")),
                ("input_payload", models.JSONField(blank=True, default=dict, verbose_name="داده‌های ورودی")),
                ("status", models.CharField(choices=[("pending", "در انتظار اجرا"), ("running", "در حال اجرا"), ("success", "موفق"), ("failed", "ناموفق"), ("needs_review", "نیازمند بررسی مدیر"), ("cancelled", "لغو شده")], db_index=True, default="pending", max_length=30, verbose_name="وضعیت")),
                ("user_friendly_status", models.CharField(blank=True, default="درخواست شما ثبت شد و در صف بررسی ربات قرار گرفت.", max_length=255, verbose_name="پیام وضعیت برای کاربر")),
                ("result_summary", models.TextField(blank=True, verbose_name="خلاصه نتیجه")),
                ("error_message_for_user", models.TextField(blank=True, verbose_name="پیام خطا برای کاربر")),
                ("technical_error", models.TextField(blank=True, verbose_name="خطای فنی")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")),
                ("started_at", models.DateTimeField(blank=True, null=True, verbose_name="زمان شروع")),
                ("finished_at", models.DateTimeField(blank=True, null=True, verbose_name="زمان پایان")),
                ("bot", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="requests", to="bot_panel.botagent", verbose_name="ربات")),
                ("command_template", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="requests", to="bot_panel.botcommandtemplate", verbose_name="نوع عملیات")),
                ("requested_by", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bot_requests", to=settings.AUTH_USER_MODEL, verbose_name="ثبت‌کننده")),
            ],
            options={"verbose_name": "درخواست ربات", "verbose_name_plural": "درخواست‌های ربات", "ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="BotRunLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("level", models.CharField(choices=[("info", "اطلاع‌رسانی"), ("warning", "هشدار"), ("error", "خطا"), ("debug", "فنی")], default="info", max_length=20, verbose_name="سطح لاگ")),
                ("message", models.TextField(verbose_name="پیام قابل مشاهده برای کاربر")),
                ("technical_message", models.TextField(blank=True, verbose_name="پیام فنی")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")),
                ("bot_request", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="logs", to="bot_panel.botrequest", verbose_name="درخواست ربات")),
            ],
            options={"verbose_name": "لاگ اجرای ربات", "verbose_name_plural": "لاگ‌های اجرای ربات", "ordering": ["created_at"]},
        ),
    ]
