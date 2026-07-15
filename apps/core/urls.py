"""Routes de l'app core (tableau de bord)."""
from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.DashboardView.as_view(), name="dashboard"),
]
