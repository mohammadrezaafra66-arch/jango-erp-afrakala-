from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("bots/", include("bot_panel.urls")),
    path("", RedirectView.as_view(pattern_name="bot_panel:dashboard", permanent=False)),
]
