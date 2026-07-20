"""Mixins de contrôle d'accès par rôle, réutilisés par toutes les vues protégées."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied

from apps.accounts.models import User


class RoleRequiredMixin(LoginRequiredMixin):
    """
    Autorise l'accès uniquement aux utilisateurs dont le rôle figure dans
    ``allowed_roles``. Doit être placé avant la vue générique dans l'ordre
    d'héritage (il combine déjà LoginRequiredMixin).
    """

    allowed_roles: tuple[str, ...] = ()

    def dispatch(self, request, *args, **kwargs):
        # Non authentifié -> comportement standard (redirection vers login).
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)

        # Les superusers passent toujours (administration technique).
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)

        if self.allowed_roles and request.user.role not in self.allowed_roles:
            messages.error(
                request,
                "Vous n'avez pas les droits nécessaires pour accéder à cette page.",
            )
            raise PermissionDenied("Rôle non autorisé.")

        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(RoleRequiredMixin):
    """Réservé au rôle Admin (gestion des utilisateurs, référentiel, demandeurs)."""

    allowed_roles = (User.Role.ADMIN,)


class VenteCreateRequiredMixin(RoleRequiredMixin):
    """
    Création de ventes : réservée à l'Admin et au Caissier.
    L'Agent est en lecture seule (il ne peut que consulter l'historique).
    """

    allowed_roles = (User.Role.ADMIN, User.Role.CAISSIER)
