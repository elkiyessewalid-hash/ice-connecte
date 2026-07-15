"""Formulaires des demandeurs (personnes physiques et morales)."""
from django import forms

from .models import DemandeurMorale, DemandeurPhysique

# Widgets communs Bootstrap
_TEXT = forms.TextInput(attrs={"class": "form-control"})
_SELECT = forms.Select(attrs={"class": "form-select"})
_CHECK = forms.CheckboxInput(attrs={"class": "form-check-input"})


class DemandeurPhysiqueForm(forms.ModelForm):
    class Meta:
        model = DemandeurPhysique
        # ``categorie`` et ``libelle`` sont calculés automatiquement dans save().
        fields = ("code", "cin", "nom", "prenom", "statut", "is_active")
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "cin": forms.TextInput(attrs={"class": "form-control"}),
            "nom": forms.TextInput(attrs={"class": "form-control"}),
            "prenom": forms.TextInput(attrs={"class": "form-control"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class DemandeurMoraleForm(forms.ModelForm):
    class Meta:
        model = DemandeurMorale
        fields = (
            "code",
            "raison_sociale",
            "nom_representant",
            "prenom_representant",
            "cin_representant",
            "statut",
            "is_active",
        )
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "raison_sociale": forms.TextInput(attrs={"class": "form-control"}),
            "nom_representant": forms.TextInput(attrs={"class": "form-control"}),
            "prenom_representant": forms.TextInput(attrs={"class": "form-control"}),
            "cin_representant": forms.TextInput(attrs={"class": "form-control"}),
            "statut": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
