"""Configuration des URLs racine du projet."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    # Authentification & gestion des utilisateurs
    path("comptes/", include("apps.accounts.urls")),
    # Modules métier
    path("referentiel/", include("apps.referentiel.urls")),
    path("demandeurs/", include("apps.demandeurs.urls")),
    path("ventes/", include("apps.ventes.urls")),
    # Tableau de bord (accueil)
    path("", include("apps.core.urls")),
]

# Service des fichiers médias (logos) en développement.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
