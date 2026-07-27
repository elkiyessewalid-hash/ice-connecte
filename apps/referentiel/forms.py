"""Formulaire du référentiel."""
from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Referentiel

_LOGO_MAX_OCTETS = 2 * 1024 * 1024  # 2 Mo
_LOGO_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


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

    def clean_logo(self):
        logo = self.cleaned_data.get("logo")
        # On ne valide que les nouveaux fichiers téléversés (pas le fichier existant).
        if isinstance(logo, UploadedFile):
            if logo.size > _LOGO_MAX_OCTETS:
                raise forms.ValidationError("Le logo ne doit pas dépasser 2 Mo.")
            extension = logo.name.rsplit(".", 1)[-1].lower() if "." in logo.name else ""
            if extension not in _LOGO_EXTENSIONS:
                raise forms.ValidationError(
                    "Format non autorisé. Utilisez png, jpg, jpeg, gif ou webp (pas de SVG)."
                )
        return logo
