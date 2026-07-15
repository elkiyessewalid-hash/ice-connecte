"""Routes des ventes."""
from django.urls import path

from . import views

app_name = "ventes"

urlpatterns = [
    path("nouvelle/", views.NouvelleVenteView.as_view(), name="nouvelle"),
    path("historique/", views.HistoriqueVentesView.as_view(), name="historique"),
    path("<int:pk>/ticket/", views.TicketView.as_view(), name="ticket"),
    path("export/excel/", views.ExportExcelView.as_view(), name="export_excel"),
    path("export/pdf/", views.ExportPdfView.as_view(), name="export_pdf"),
]
