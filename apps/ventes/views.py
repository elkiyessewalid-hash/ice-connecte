"""Vues des ventes : saisie, historique, ticket imprimable et exports."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView

from apps.referentiel.models import Referentiel

from .exports import export_ventes_excel, export_ventes_pdf
from .forms import VenteForm
from .models import Vente
from .services import peek_prochain_code


# ---------------------------------------------------------------------------
# Saisie d'une nouvelle vente
# ---------------------------------------------------------------------------
class NouvelleVenteView(LoginRequiredMixin, CreateView):
    """
    Écran « Nouvelle Vente ». Accessible aux trois rôles.
    Le prix unitaire et le référentiel proviennent du référentiel actif ;
    la quantité est recalculée côté serveur (Prix total / Prix unitaire).
    """

    model = Vente
    form_class = VenteForm
    template_name = "ventes/nouvelle_vente.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["referentiel_actif"] = Referentiel.get_active()
        return kwargs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        referentiel = Referentiel.get_active()
        ctx["referentiel_actif"] = referentiel
        ctx["code_preview"] = peek_prochain_code(referentiel) if referentiel else "—"
        # Affichage du ticket après enregistrement (motif Post/Redirect/Get).
        ticket_id = self.request.GET.get("ticket")
        if ticket_id:
            ctx["ticket_vente"] = Vente.objects.filter(pk=ticket_id).select_related(
                "demandeur", "referentiel", "utilisateur"
            ).first()
        return ctx

    def form_valid(self, form):
        referentiel = form.referentiel_actif  # garanti non nul par le form.clean()
        vente = form.save(commit=False)
        vente.referentiel = referentiel
        vente.prix_unitaire = referentiel.prix_unitaire
        vente.quantite = form.cleaned_data["quantite"]
        vente.utilisateur = self.request.user
        vente.save()  # attribue le code_vente
        messages.success(self.request, f"Vente {vente.code_vente} enregistrée.")
        # Redirige vers le formulaire en demandant l'ouverture du ticket.
        return redirect(f"{reverse('ventes:nouvelle')}?ticket={vente.pk}")


# ---------------------------------------------------------------------------
# Ticket imprimable
# ---------------------------------------------------------------------------
class TicketView(LoginRequiredMixin, DetailView):
    """Page autonome, optimisée pour l'impression, d'un ticket de vente."""

    model = Vente
    template_name = "ventes/ticket.html"
    context_object_name = "vente"

    def get_queryset(self):
        return super().get_queryset().select_related("demandeur", "referentiel", "utilisateur")


# ---------------------------------------------------------------------------
# Historique + exports
# ---------------------------------------------------------------------------
def filtrer_ventes(request):
    """Applique les filtres de la barre d'historique et renvoie le queryset."""
    qs = Vente.objects.select_related("demandeur", "referentiel", "utilisateur").all()

    date_debut = request.GET.get("date_debut", "").strip()
    date_fin = request.GET.get("date_fin", "").strip()
    demandeur = request.GET.get("demandeur", "").strip()
    type_dem = request.GET.get("type", "").strip()
    code = request.GET.get("code", "").strip()

    if date_debut:
        qs = qs.filter(date_vente__gte=date_debut)
    if date_fin:
        qs = qs.filter(date_vente__lte=date_fin)
    if demandeur:
        qs = qs.filter(
            Q(demandeur__libelle__icontains=demandeur) | Q(demandeur__code__icontains=demandeur)
        )
    if type_dem:
        qs = qs.filter(demandeur__categorie=type_dem)
    if code:
        qs = qs.filter(code_vente__icontains=code)
    return qs


class HistoriqueVentesView(LoginRequiredMixin, ListView):
    """Historique des ventes (tous rôles) avec filtres serveur + DataTables."""

    template_name = "ventes/historique.html"
    context_object_name = "ventes"

    def get_queryset(self):
        return filtrer_ventes(self.request)

    def get_context_data(self, **kwargs):
        from apps.demandeurs.models import Demandeur

        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Demandeur.Categorie.choices
        ctx["filtres"] = {
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
            "demandeur": self.request.GET.get("demandeur", ""),
            "type": self.request.GET.get("type", ""),
            "code": self.request.GET.get("code", ""),
        }
        return ctx


class ExportExcelView(LoginRequiredMixin, View):
    """Export Excel de l'historique filtré."""

    def get(self, request, *args, **kwargs):
        return export_ventes_excel(filtrer_ventes(request))


class ExportPdfView(LoginRequiredMixin, View):
    """Export PDF de l'historique filtré."""

    def get(self, request, *args, **kwargs):
        return export_ventes_pdf(filtrer_ventes(request))
