"""Formulaire de saisie d'une vente."""
from django import forms
from django.utils import timezone

from apps.demandeurs.models import Demandeur

from .models import Vente
from .services import calc_prix_total, calc_quantite


class VenteForm(forms.ModelForm):
    """
    Saisie d'une vente. L'utilisateur choisit un demandeur (via la modale) puis
    saisit **soit le prix total, soit la quantité** ; l'autre valeur est calculée
    à partir du prix unitaire du référentiel actif (source de vérité serveur).

    Le champ caché ``saisie`` indique lequel des deux l'utilisateur a piloté, afin
    de conserver exactement sa valeur et d'en déduire l'autre sans dérive d'arrondi.
    """

    demandeur = forms.ModelChoiceField(
        queryset=Demandeur.objects.filter(is_active=True),
        widget=forms.HiddenInput,
        error_messages={"required": "Veuillez sélectionner un demandeur."},
    )

    class Meta:
        model = Vente
        fields = ("demandeur", "prix_total", "quantite", "date_vente")
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
            "quantite": forms.NumberInput(
                attrs={
                    "class": "form-control form-control-lg",
                    "step": "0.001",
                    "min": "0.001",
                    "placeholder": "0.000",
                    "id": "id_quantite",
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
        # Les deux champs sont optionnels : un seul suffit, l'autre est calculé.
        self.fields["prix_total"].required = False
        self.fields["quantite"].required = False
        if not self.initial.get("date_vente"):
            self.initial["date_vente"] = timezone.localdate()

    def clean_date_vente(self):
        # Interdit les dates futures : elles fausseraient l'ordre et la
        # numérotation annuelle des ventes.
        date_vente = self.cleaned_data.get("date_vente")
        if date_vente and date_vente > timezone.localdate():
            raise forms.ValidationError("La date de vente ne peut pas être dans le futur.")
        return date_vente

    def clean(self):
        cleaned = super().clean()
        # Le référentiel actif est indispensable pour tarifer la vente.
        if not self.referentiel_actif:
            raise forms.ValidationError(
                "Aucun référentiel actif : impossible d'enregistrer une vente. "
                "Demandez à un administrateur d'activer un référentiel."
            )
        pu = self.referentiel_actif.prix_unitaire
        prix_total = cleaned.get("prix_total")
        quantite = cleaned.get("quantite")
        saisie = (self.data.get("saisie") or "").strip()

        # On préserve la valeur saisie par l'utilisateur et on calcule l'autre.
        if saisie == "quantite" and quantite and quantite > 0:
            cleaned["quantite"] = quantite
            cleaned["prix_total"] = calc_prix_total(quantite, pu)
        elif prix_total and prix_total > 0:
            cleaned["prix_total"] = prix_total
            cleaned["quantite"] = calc_quantite(prix_total, pu)
        elif quantite and quantite > 0:
            cleaned["quantite"] = quantite
            cleaned["prix_total"] = calc_prix_total(quantite, pu)
        else:
            raise forms.ValidationError(
                "Saisissez un prix total ou une quantité (valeur strictement positive)."
            )
        return cleaned
