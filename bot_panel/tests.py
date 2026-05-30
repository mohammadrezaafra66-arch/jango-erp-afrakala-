from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import BotAgent, BotCommandTemplate, BotRequest, BotRunLog


class BotPanelMvpTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="normal-user", password="pass12345")
        self.staff = User.objects.create_user(username="staff-user", password="pass12345", is_staff=True)
        self.agent = BotAgent.objects.create(name="ربات بروزرسانی قیمت", slug="price-update-bot")
        self.command = BotCommandTemplate.objects.create(bot=self.agent, title="بروزرسانی قیمت", code="update-price")

    def test_user_can_create_bot_request(self):
        self.client.login(username="normal-user", password="pass12345")
        response = self.client.post(reverse("bot_panel:request_create"), data={
            "bot": self.agent.id,
            "command_template": self.command.id,
            "title": "تست بروزرسانی قیمت",
            "user_message": "لطفاً قیمت‌های امروز بررسی شود.",
            "input_payload_text": "برند: LG",
        })
        self.assertEqual(response.status_code, 302)
        bot_request = BotRequest.objects.get(title="تست بروزرسانی قیمت")
        self.assertEqual(bot_request.requested_by, self.user)
        self.assertEqual(bot_request.status, "pending")
        self.assertEqual(bot_request.logs.count(), 1)

    def test_normal_user_sees_only_own_requests(self):
        other_user = get_user_model().objects.create_user(username="other", password="pass12345")
        BotRequest.objects.create(requested_by=self.user, bot=self.agent, command_template=self.command, title="درخواست خودم")
        BotRequest.objects.create(requested_by=other_user, bot=self.agent, command_template=self.command, title="درخواست دیگران")
        self.client.login(username="normal-user", password="pass12345")
        response = self.client.get(reverse("bot_panel:request_list"))
        self.assertContains(response, "درخواست خودم")
        self.assertNotContains(response, "درخواست دیگران")

    def test_staff_sees_all_requests(self):
        other_user = get_user_model().objects.create_user(username="other", password="pass12345")
        BotRequest.objects.create(requested_by=self.user, bot=self.agent, command_template=self.command, title="درخواست کاربر عادی")
        BotRequest.objects.create(requested_by=other_user, bot=self.agent, command_template=self.command, title="درخواست کاربر دیگر")
        self.client.login(username="staff-user", password="pass12345")
        response = self.client.get(reverse("bot_panel:request_list"))
        self.assertContains(response, "درخواست کاربر عادی")
        self.assertContains(response, "درخواست کاربر دیگر")

    def test_technical_log_is_hidden_from_normal_user(self):
        bot_request = BotRequest.objects.create(requested_by=self.user, bot=self.agent, command_template=self.command, title="درخواست تست لاگ")
        BotRunLog.objects.create(bot_request=bot_request, level="error", message="ربات نتوانست درخواست را کامل کند.", technical_message="ConnectionError: timeout")
        self.client.login(username="normal-user", password="pass12345")
        response = self.client.get(reverse("bot_panel:request_detail", kwargs={"pk": bot_request.pk}))
        self.assertContains(response, "ربات نتوانست درخواست را کامل کند.")
        self.assertNotContains(response, "ConnectionError")
