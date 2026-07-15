"""Formulaire de saisie d'une vente."""
from django import forms
from django.utils import timezone

from apps.demandeurs.models import Demandeur

from .models import Vente
from .services import calc_quantite


class VenteForm(forms.ModelForm):
    """
    Saisie d'une vente. L'utilisateur choisit un demandeur (via la modale) et
    saisit le **prix total** ; la quantité et le prix unitaire sont déterminés
    côté serveur à partir du référentiel actif (source de vérité).
    """

    demandeur = forms.ModelChoiceField(
        queryset=Demandeur.objects.filter(is_active=True),
        widget=forms.HiddenInput,
        error_messages={"required": "Veuillez sélectionner un demandeur."},
    )

    class Meta:
        model = Vente
        fields = ("demandeur", "prix_total", "date_vente")
        widgets = {
            "prix_total": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "step": "0.01",
                    "min": "0.01",
                    "placeholder": "0.00",
                    "id": "id_prix_total",
                }
            ),
            "date_vente": forms.DateInput(
                attrs={"class": "form-control", "type": "date", "id": "id_date_vente"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, referentiel_actif=None, **kwargs):
        self.referentiel_actif = referentiel_actif
        super().__init__(*args, **kwargs)
        if not self.initial.get("date_vente"):
            self.initial["date_vente"] = timezone.localdate()

    def clean_prix_total(self):
        prix_total = self.cleaned_data["prix_total"]
        if prix_total is None or prix_total <= 0:
            raise forms.ValidationError("Le prix total doit être strictement positif.")
        return prix_total

    def clean(self):
        cleaned = super().clean()
        # Le référentiel actif est indispensable pour tarifer la vente.
        if not self.referentiel_actif:
            raise forms.ValidationError(
                "Aucun référentiel actif : impossible d'enregistrer une vente. "
                "Demandez à un administrateur d'activer un référentiel."
            )
        prix_total = cleaned.get("prix_total")
        if prix_total is not None:
            pu = self.referentiel_actif.prix_unitaire
            # Quantité recalculée côté serveur (ne fait pas confiance au client).
            cleaned["quantite"] = calc_quantite(prix_total, pu)
        return cleaned
