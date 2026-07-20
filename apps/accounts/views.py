"""Vues d'authentification et de gestion des utilisateurs (CRUD réservé Admin)."""
from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import LoginForm, UserCreateForm, UserUpdateForm
from .mixins import AdminRequiredMixin
from .models import User


# ---------------------------------------------------------------------------
# Authentification
# ---------------------------------------------------------------------------
class LoginView(auth_views.LoginView):
    """Page de connexion. Redirige selon le rôle après authentification."""

    template_name = "registration/login.html"
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        # Respecte ?next= si présent, sinon redirige selon le rôle.
        url = self.get_redirect_url()
        if url:
            return url
        return reverse(self.request.user.role_home_url_name())


class LogoutView(auth_views.LogoutView):
    """Déconnexion (POST) puis retour à la page de connexion."""

    next_page = reverse_lazy("accounts:login")


# ---------------------------------------------------------------------------
# Gestion des utilisateurs — CRUD (Admin uniquement)
# ---------------------------------------------------------------------------
class UserListView(AdminRequiredMixin, ListView):
    model = User
    template_name = "accounts/user_list.html"
    partial_template_name = "accounts/_user_table.html"
    context_object_name = "utilisateurs"
    paginate_by = 5

    def get_queryset(self):
        qs = super().get_queryset()
        recherche = self.request.GET.get("q", "").strip()
        if recherche:
            qs = qs.filter(
                Q(username__icontains=recherche)
                | Q(last_name__icontains=recherche)
                | Q(first_name__icontains=recherche)
            )
        role = self.request.GET.get("role", "").strip()
        if role in User.Role.values:
            qs = qs.filter(role=role)
        etat = self.request.GET.get("etat", "").strip()
        if etat == "actif":
            qs = qs.filter(is_active=True)
        elif etat == "inactif":
            qs = qs.filter(is_active=False)
        return qs.distinct()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["roles"] = User.Role.choices
        ctx["filtres"] = {
            "q": self.request.GET.get("q", ""),
            "role": self.request.GET.get("role", ""),
            "etat": self.request.GET.get("etat", ""),
        }
        return ctx

    def get_template_names(self):
        # Requête HTMX -> on ne renvoie que le fragment (tableau + pagination).
        if self.request.headers.get("HX-Request"):
            return [self.partial_template_name]
        return [self.template_name]


class UserDetailView(AdminRequiredMixin, DetailView):
    """Fragment de consultation d'un utilisateur, chargé dans la modale générique."""

    model = User
    template_name = "accounts/_user_detail.html"
    context_object_name = "utilisateur"


class UserCreateView(AdminRequiredMixin, CreateView):
    model = User
    form_class = UserCreateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        messages.success(self.request, "Utilisateur créé avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre"] = "Nouvel utilisateur"
        return ctx


class UserUpdateView(AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = "accounts/user_form.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        messages.success(self.request, "Utilisateur mis à jour avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre"] = f"Modifier — {self.object}"
        return ctx


class UserDeleteView(AdminRequiredMixin, DeleteView):
    model = User
    template_name = "accounts/user_confirm_delete.html"
    success_url = reverse_lazy("accounts:user_list")

    def form_valid(self, form):
        # Empêche un admin de supprimer son propre compte.
        if self.get_object() == self.request.user:
            messages.error(self.request, "Vous ne pouvez pas supprimer votre propre compte.")
            return redirect(self.success_url)
        messages.success(self.request, "Utilisateur supprimé.")
        return super().form_valid(form)
