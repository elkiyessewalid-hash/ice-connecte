"""Enregistrement du modèle User dans l'administration Django."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Administration des utilisateurs, avec le champ ``role`` intégré."""

    list_display = ("username", "last_name", "first_name", "role", "is_active", "is_staff")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("username", "last_name", "first_name")
    ordering = ("last_name", "first_name")

    # Ajoute la section « Rôle métier » aux fiches existantes.
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Rôle métier", {"fields": ("role",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Rôle métier", {"fields": ("role",)}),
    )
