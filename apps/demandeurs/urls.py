"""Routes des demandeurs (CRUD + recherche JSON)."""
from django.urls import path

from . import api, views

app_name = "demandeurs"

urlpatterns = [
    path("", views.DemandeurListView.as_view(), name="list"),
    # Personne physique
    path("physique/nouveau/", views.DemandeurPhysiqueCreateView.as_view(), name="physique_create"),
    path("physique/<int:pk>/modifier/", views.DemandeurPhysiqueUpdateView.as_view(), name="physique_update"),
    # Personne morale
    path("morale/nouveau/", views.DemandeurMoraleCreateView.as_view(), name="morale_create"),
    path("morale/<int:pk>/modifier/", views.DemandeurMoraleUpdateView.as_view(), name="morale_update"),
    # Actions
    path("<int:pk>/supprimer/", views.DemandeurDeleteView.as_view(), name="delete"),
    path("<int:pk>/basculer-actif/", views.DemandeurToggleActiveView.as_view(), name="toggle_active"),
    # API
    path("recherche/", api.DemandeurSearchView.as_view(), name="search"),
]
