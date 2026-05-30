from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import BotRequestForm
from .models import BotAgent, BotRequest
from .services import run_bot_request


def can_view_technical(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


class RequestScopeMixin:
    def get_scoped_requests(self):
        qs = BotRequest.objects.select_related("requested_by", "bot", "command_template")
        if can_view_technical(self.request.user):
            return qs
        return qs.filter(requested_by=self.request.user)


class BotDashboardView(LoginRequiredMixin, RequestScopeMixin, TemplateView):
    template_name = "bot_panel/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = self.get_scoped_requests()
        context["active_bot_count"] = BotAgent.objects.filter(is_active=True).count()
        context["pending_count"] = qs.filter(status="pending").count()
        context["success_count"] = qs.filter(status="success").count()
        context["failed_count"] = qs.filter(status="failed").count()
        context["latest_requests"] = qs[:8]
        return context


class BotAgentListView(LoginRequiredMixin, ListView):
    template_name = "bot_panel/agent_list.html"
    context_object_name = "agents"

    def get_queryset(self):
        qs = BotAgent.objects.all()
        if can_view_technical(self.request.user):
            return qs
        return qs.filter(is_active=True)


class BotRequestListView(LoginRequiredMixin, RequestScopeMixin, ListView):
    template_name = "bot_panel/request_list.html"
    context_object_name = "bot_requests"
    paginate_by = 20

    def get_queryset(self):
        return self.get_scoped_requests()


class BotRequestCreateView(LoginRequiredMixin, CreateView):
    template_name = "bot_panel/request_form.html"
    form_class = BotRequestForm
    success_url = reverse_lazy("bot_panel:request_list")

    def form_valid(self, form):
        form.instance.requested_by = self.request.user
        response = super().form_valid(form)
        run_bot_request(self.object)
        messages.success(self.request, "درخواست شما ثبت شد و در صف بررسی ربات قرار گرفت.")
        return response


class BotRequestDetailView(LoginRequiredMixin, DetailView):
    template_name = "bot_panel/request_detail.html"
    context_object_name = "bot_request"

    def get_queryset(self):
        qs = BotRequest.objects.select_related("requested_by", "bot", "command_template").prefetch_related("logs")
        if can_view_technical(self.request.user):
            return qs
        return qs.filter(requested_by=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_view_technical_logs"] = can_view_technical(self.request.user)
        return context


def create_request_for_agent(request, agent_id):
    return redirect(f"{reverse_lazy('bot_panel:request_create')}?bot={agent_id}")
