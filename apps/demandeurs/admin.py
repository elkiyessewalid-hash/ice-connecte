"""Administration des demandeurs."""
from django.contrib import admin

from .models import DemandeurMorale, DemandeurPhysique


@admin.register(DemandeurPhysique)
class DemandeurPhysiqueAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "prenom", "cin", "statut", "is_active")
    list_filter = ("statut", "is_active")
    search_fields = ("code", "nom", "prenom", "cin")
    readonly_fields = ("categorie", "libelle", "created_at", "updated_at")


@admin.register(DemandeurMorale)
class DemandeurMoraleAdmin(admin.ModelAdmin):
    list_display = ("code", "raison_sociale", "nom_representant", "statut", "is_active")
    list_filter = ("statut", "is_active")
    search_fields = ("code", "raison_sociale", "nom_representant", "cin_representant")
    readonly_fields = ("categorie", "libelle", "created_at", "updated_at")
