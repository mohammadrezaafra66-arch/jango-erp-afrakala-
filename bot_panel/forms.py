from django import forms

from .models import BotAgent, BotCommandTemplate, BotRequest


class BotRequestForm(forms.ModelForm):
    bot = forms.ModelChoiceField(
        label="ربات",
        queryset=BotAgent.objects.filter(is_active=True),
        empty_label="یک ربات را انتخاب کنید",
    )
    command_template = forms.ModelChoiceField(
        label="نوع عملیات",
        queryset=BotCommandTemplate.objects.filter(is_active=True, bot__is_active=True),
        empty_label="نوع عملیات را انتخاب کنید",
    )
    input_payload_text = forms.CharField(
        label="اطلاعات تکمیلی",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
        help_text="اطلاعات تکمیلی را ساده و فارسی بنویسید؛ مثلاً برند، مدل، نام مشتری یا بازه قیمت.",
    )

    class Meta:
        model = BotRequest
        fields = ["bot", "command_template", "title", "user_message", "input_payload_text"]
        labels = {"title": "عنوان درخواست", "user_message": "توضیح درخواست"}
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "مثلاً: بروزرسانی قیمت کولر گازی"}),
            "user_message": forms.Textarea(attrs={"rows": 5, "placeholder": "درخواست خود را با زبان ساده بنویسید."}),
        }

    def clean(self):
        cleaned_data = super().clean()
        bot = cleaned_data.get("bot")
        command_template = cleaned_data.get("command_template")
        if bot and command_template and command_template.bot_id != bot.id:
            raise forms.ValidationError("نوع عملیات انتخاب‌شده برای این ربات تعریف نشده است.")
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        text = self.cleaned_data.get("input_payload_text", "").strip()
        instance.input_payload = {"متن کاربر": text} if text else {}
        if commit:
            instance.save()
        return instance
