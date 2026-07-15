"""Administration des ventes."""
from django.contrib import admin

from .models import SequenceCounter, Vente


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = (
        "code_vente",
        "demandeur",
        "quantite",
        "prix_unitaire",
        "prix_total",
        "date_vente",
        "utilisateur",
    )
    list_filter = ("date_vente", "referentiel", "utilisateur")
    search_fields = ("code_vente", "demandeur__libelle", "demandeur__code")
    readonly_fields = ("code_vente", "created_at")
    date_hierarchy = "date_vente"


@admin.register(SequenceCounter)
class SequenceCounterAdmin(admin.ModelAdmin):
    list_display = ("annee", "dernier_numero")
