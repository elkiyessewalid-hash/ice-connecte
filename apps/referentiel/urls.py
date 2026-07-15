"""Routes du référentiel."""
from django.urls import path

from . import views

app_name = "referentiel"

urlpatterns = [
    path("", views.ReferentielListView.as_view(), name="list"),
    path("nouveau/", views.ReferentielCreateView.as_view(), name="create"),
    path("<int:pk>/modifier/", views.ReferentielUpdateView.as_view(), name="update"),
    path("<int:pk>/supprimer/", views.ReferentielDeleteView.as_view(), name="delete"),
    path("<int:pk>/activer/", views.ReferentielActivateView.as_view(), name="activate"),
]
