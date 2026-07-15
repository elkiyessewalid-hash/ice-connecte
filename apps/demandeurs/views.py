"""Vues des demandeurs : CRUD (Admin) + activation/désactivation."""
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.accounts.mixins import AdminRequiredMixin

from .forms import DemandeurMoraleForm, DemandeurPhysiqueForm
from .models import Demandeur, DemandeurMorale, DemandeurPhysique


class DemandeurListView(AdminRequiredMixin, ListView):
    model = Demandeur
    template_name = "demandeurs/demandeur_list.html"
    context_object_name = "demandeurs"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        categorie = self.request.GET.get("categorie", "").strip()
        if categorie in Demandeur.Categorie.values:
            qs = qs.filter(categorie=categorie)
        return qs


# --- Personne physique -----------------------------------------------------
class DemandeurPhysiqueCreateView(AdminRequiredMixin, CreateView):
    model = DemandeurPhysique
    form_class = DemandeurPhysiqueForm
    template_name = "demandeurs/demandeur_form.html"
    success_url = reverse_lazy("demandeurs:list")

    def form_valid(self, form):
        messages.success(self.request, "Demandeur (personne physique) créé.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre"] = "Nouveau demandeur — personne physique"
        return ctx


class DemandeurPhysiqueUpdateView(AdminRequiredMixin, UpdateView):
    model = DemandeurPhysique
    form_class = DemandeurPhysiqueForm
    template_name = "demandeurs/demandeur_form.html"
    success_url = reverse_lazy("demandeurs:list")

    def form_valid(self, form):
        messages.success(self.request, "Demandeur mis à jour.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre"] = f"Modifier — {self.object.libelle}"
        return ctx


# --- Personne morale -------------------------------------------------------
class DemandeurMoraleCreateView(AdminRequiredMixin, CreateView):
    model = DemandeurMorale
    form_class = DemandeurMoraleForm
    template_name = "demandeurs/demandeur_form.html"
    success_url = reverse_lazy("demandeurs:list")

    def form_valid(self, form):
        messages.success(self.request, "Demandeur (personne morale) créé.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre"] = "Nouveau demandeur — personne morale"
        return ctx


class DemandeurMoraleUpdateView(AdminRequiredMixin, UpdateView):
    model = DemandeurMorale
    form_class = DemandeurMoraleForm
    template_name = "demandeurs/demandeur_form.html"
    success_url = reverse_lazy("demandeurs:list")

    def form_valid(self, form):
        messages.success(self.request, "Demandeur mis à jour.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre"] = f"Modifier — {self.object.libelle}"
        return ctx


# --- Actions ---------------------------------------------------------------
class DemandeurDeleteView(AdminRequiredMixin, DeleteView):
    model = Demandeur
    template_name = "demandeurs/demandeur_confirm_delete.html"
    success_url = reverse_lazy("demandeurs:list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Impossible de supprimer ce demandeur : des ventes lui sont rattachées. "
                "Vous pouvez le désactiver à la place.",
            )
            return redirect(self.success_url)
        messages.success(self.request, "Demandeur supprimé.")
        return response


class DemandeurToggleActiveView(AdminRequiredMixin, View):
    """Active / désactive un demandeur (POST)."""

    def post(self, request, pk):
        demandeur = get_object_or_404(Demandeur, pk=pk)
        demandeur.is_active = not demandeur.is_active
        demandeur.save(update_fields=["is_active", "updated_at"])
        etat = "activé" if demandeur.is_active else "désactivé"
        messages.success(request, f"Demandeur {etat}.")
        return redirect("demandeurs:list")
