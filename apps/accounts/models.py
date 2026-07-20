"""Modèle utilisateur personnalisé avec gestion des rôles métier."""
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models


class User(AbstractUser):
    """
    Utilisateur de l'application.

    On réutilise les champs standards de Django :
      - ``username``   -> le « Login »   (30 caractères max)
      - ``first_name`` -> le « Prénom »  (25 caractères max)
      - ``last_name``  -> le « Nom »     (25 caractères max)
      - ``password``   -> haché automatiquement par Django
    et on ajoute un champ ``role`` qui pilote les permissions métier.
    """

    username = models.CharField(
        "Login",
        max_length=30,
        unique=True,
        validators=[UnicodeUsernameValidator()],
        error_messages={"unique": "Un utilisateur avec ce login existe déjà."},
        help_text="30 caractères maximum.",
    )
    first_name = models.CharField("Prénom", max_length=25, blank=True)
    last_name = models.CharField("Nom", max_length=25, blank=True)

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        AGENT = "AGENT", "Agent"
        CAISSIER = "CAISSIER", "Caissier"

    role = models.CharField(
        "Rôle",
        max_length=10,
        choices=Role.choices,
        default=Role.AGENT,
        help_text="Détermine les écrans et actions accessibles.",
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["last_name", "first_name", "username"]

    def __str__(self):
        nom_complet = self.get_full_name()
        return f"{nom_complet} ({self.username})" if nom_complet else self.username

    # -- Aides de rôle (utilisées par les vues, mixins et templates) --
    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN

    @property
    def is_agent(self) -> bool:
        return self.role == self.Role.AGENT

    @property
    def is_caissier(self) -> bool:
        return self.role == self.Role.CAISSIER

    def role_home_url_name(self) -> str:
        """Nom d'URL de la page d'accueil selon le rôle (redirection post-login)."""
        if self.is_admin:
            return "core:dashboard"
        if self.is_caissier:
            # Le caissier peut créer des ventes : il arrive sur la saisie.
            return "ventes:nouvelle"
        # L'agent est en lecture seule : il arrive sur l'historique.
        return "ventes:historique"
