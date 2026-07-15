"""Administration du référentiel."""
from django.contrib import admin

from .models import Referentiel


@admin.register(Referentiel)
class ReferentielAdmin(admin.ModelAdmin):
    list_display = ("code", "nom", "ville", "prix_unitaire", "is_active")
    list_filter = ("is_active", "ville")
    search_fields = ("code", "nom", "ville")
    readonly_fields = ("created_at", "updated_at")
