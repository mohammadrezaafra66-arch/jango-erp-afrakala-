from django.urls import path
from . import views

app_name = "bot_panel"

urlpatterns = [
    path("", views.BotDashboardView.as_view(), name="dashboard"),
    path("agents/", views.BotAgentListView.as_view(), name="agent_list"),
    path("agents/<int:agent_id>/request/", views.create_request_for_agent, name="request_for_agent"),
    path("requests/", views.BotRequestListView.as_view(), name="request_list"),
    path("requests/new/", views.BotRequestCreateView.as_view(), name="request_create"),
    path("requests/<int:pk>/", views.BotRequestDetailView.as_view(), name="request_detail"),
]
