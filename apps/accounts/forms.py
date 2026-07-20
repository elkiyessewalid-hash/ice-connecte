"""Formulaires d'authentification et de gestion des utilisateurs."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password

from .models import User


class LoginForm(AuthenticationForm):
    """Formulaire de connexion (Login + Mot de passe) stylé Bootstrap."""

    username = forms.CharField(
        label="Login",
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Votre login",
                "autofocus": True,
                "autocomplete": "username",
            }
        ),
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control form-control-lg",
                "placeholder": "Votre mot de passe",
                "autocomplete": "current-password",
            }
        ),
    )

    error_messages = {
        "invalid_login": "Login ou mot de passe incorrect.",
        "inactive": "Ce compte est désactivé.",
    }


class _BaseUserForm(forms.ModelForm):
    """Champs communs aux formulaires de création et de modification d'utilisateur."""

    class Meta:
        model = User
        fields = ("username", "last_name", "first_name", "role", "is_active")
        labels = {
            "username": "Login",
            "last_name": "Nom",
            "first_name": "Prénom",
            "role": "Rôle",
            "is_active": "Compte actif",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class UserCreateForm(_BaseUserForm):
    """Création d'un utilisateur : Login, Mot de passe, Nom, Prénom, Rôle."""

    password1 = forms.CharField(
        label="Mot de passe",
        max_length=20,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        max_length=20,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    def clean_password2(self):
        pwd1 = self.cleaned_data.get("password1")
        pwd2 = self.cleaned_data.get("password2")
        if pwd1 and pwd2 and pwd1 != pwd2:
            raise forms.ValidationError("Les deux mots de passe ne correspondent pas.")
        # Applique les validateurs de robustesse configurés dans settings.
        validate_password(pwd2)
        return pwd2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])  # hachage
        if commit:
            user.save()
        return user


class UserUpdateForm(_BaseUserForm):
    """
    Modification d'un utilisateur. Le mot de passe est optionnel :
    laissé vide, il reste inchangé.
    """

    password1 = forms.CharField(
        label="Nouveau mot de passe",
        required=False,
        max_length=20,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
        help_text="Laisser vide pour conserver le mot de passe actuel.",
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        required=False,
        max_length=20,
        widget=forms.PasswordInput(attrs={"class": "form-control", "autocomplete": "new-password"}),
    )

    def clean(self):
        cleaned = super().clean()
        pwd1 = cleaned.get("password1")
        pwd2 = cleaned.get("password2")
        if pwd1 or pwd2:
            if pwd1 != pwd2:
                self.add_error("password2", "Les deux mots de passe ne correspondent pas.")
            else:
                validate_password(pwd1, self.instance)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        new_password = self.cleaned_data.get("password1")
        if new_password:
            user.set_password(new_password)
        if commit:
            user.save()
        return user
