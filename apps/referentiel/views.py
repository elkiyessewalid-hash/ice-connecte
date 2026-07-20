"""CRUD du référentiel (réservé au rôle Admin) + action d'activation."""
from django.contrib import messages
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.accounts.mixins import AdminRequiredMixin

from .forms import ReferentielForm
from .models import Referentiel


class ReferentielListView(AdminRequiredMixin, ListView):
    model = Referentiel
    template_name = "referentiel/referentiel_list.html"
    context_object_name = "referentiels"
    paginate_by = 25


class ReferentielCreateView(AdminRequiredMixin, CreateView):
    model = Referentiel
    form_class = ReferentielForm
    template_name = "referentiel/referentiel_form.html"
    success_url = reverse_lazy("referentiel:list")

    def dispatch(self, request, *args, **kwargs):
        # Règle métier : un seul référentiel, pas de création multiple.
        existant = Referentiel.objects.first()
        if existant is not None and request.user.is_authenticated:
            messages.info(
                request,
                "Un référentiel existe déjà : il n'est pas possible d'en créer un "
                "second. Vous pouvez le modifier.",
            )
            return redirect("referentiel:update", pk=existant.pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        # Le référentiel unique est toujours actif (source de prix des ventes).
        form.instance.is_active = True
        messages.success(self.request, "Référentiel créé avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre"] = "Nouveau référentiel"
        return ctx


class ReferentielUpdateView(AdminRequiredMixin, UpdateView):
    model = Referentiel
    form_class = ReferentielForm
    template_name = "referentiel/referentiel_form.html"
    success_url = reverse_lazy("referentiel:list")

    def form_valid(self, form):
        messages.success(self.request, "Référentiel mis à jour.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["titre"] = f"Modifier — {self.object.code}"
        return ctx


class ReferentielDeleteView(AdminRequiredMixin, DeleteView):
    model = Referentiel
    template_name = "referentiel/referentiel_confirm_delete.html"
    success_url = reverse_lazy("referentiel:list")

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                "Impossible de supprimer ce référentiel : des ventes y sont "
                "rattachées. L'historique doit rester tarifé.",
            )
            return redirect(self.success_url)
        messages.success(self.request, "Référentiel supprimé.")
        return response


class ReferentielActivateView(AdminRequiredMixin, View):
    """Active un référentiel (désactive automatiquement les autres)."""

    def post(self, request, pk):
        referentiel = get_object_or_404(Referentiel, pk=pk)
        referentiel.is_active = True
        referentiel.save()
        messages.success(request, f"« {referentiel.code} » est désormais le référentiel actif.")
        return redirect("referentiel:list")
