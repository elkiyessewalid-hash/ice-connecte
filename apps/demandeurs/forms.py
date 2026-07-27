"""Formulaires des demandeurs (personnes physiques et morales)."""
from django import forms

from .models import DemandeurMorale, DemandeurPhysique

# Widgets communs Bootstrap
_TEXT = forms.TextInput(attrs={"class": "form-control"})
_SELECT = forms.Select(attrs={"class": "form-select"})
_CHECK = forms.CheckboxInput(attrs={"class": "form-check-input"})

_CIN_DEJA_UTILISE = "Ce CIN est déjà utilisé par un autre demandeur."


def _cin_deja_pris(cin, *, exclure_physique=None, exclure_morale=None) -> bool:
    """
    Vrai si ``cin`` existe déjà, que ce soit comme CIN d'une personne physique
    ou comme CIN du représentant d'une personne morale. L'unicité du CIN est
    ainsi garantie **à travers les deux tables** (physique + morale), sans tenir
    compte de la casse ni des espaces.
    """
    cin = (cin or "").strip()
    physiques = DemandeurPhysique.objects.filter(cin__iexact=cin)
    morales = DemandeurMorale.objects.filter(cin_representant__iexact=cin)
    if exclure_physique is not None:
        physiques = physiques.exclude(pk=exclure_physique)
    if exclure_morale is not None:
        morales = morales.exclude(pk=exclure_morale)
    return physiques.exists() or morales.exists()


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

    def clean_cin(self):
        cin = (self.cleaned_data.get("cin") or "").strip().upper()
        if cin and _cin_deja_pris(cin, exclure_physique=self.instance.pk):
            raise forms.ValidationError(_CIN_DEJA_UTILISE)
        return cin


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

    def clean_cin_representant(self):
        cin = (self.cleaned_data.get("cin_representant") or "").strip().upper()
        if cin and _cin_deja_pris(cin, exclure_morale=self.instance.pk):
            raise forms.ValidationError(_CIN_DEJA_UTILISE)
        return cin
