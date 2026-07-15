"""Formulaire du référentiel."""
from django import forms

from .models import Referentiel


class ReferentielForm(forms.ModelForm):
    class Meta:
        model = Referentiel
        fields = ("code", "nom", "ville", "prix_unitaire", "logo", "is_active")
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control", "placeholder": "ex : 8234"}),
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "ville": forms.TextInput(attrs={"class": "form-control"}),
            "prix_unitaire": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_prix_unitaire(self):
        prix = self.cleaned_data["prix_unitaire"]
        if prix is not None and prix <= 0:
            raise forms.ValidationError("Le prix unitaire doit être strictement positif.")
        return prix
