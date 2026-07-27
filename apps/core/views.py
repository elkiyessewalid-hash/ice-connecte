"""Tableau de bord : cartes d'agrégats, ventes récentes et données de graphiques."""
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Sum
from django.utils import timezone
from django.views.generic import TemplateView


class DashboardView(LoginRequiredMixin, TemplateView):
    """Page d'accueil après connexion. Synthétise l'activité commerciale."""

    template_name = "core/dashboard.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # Imports locaux : les modèles Vente/Demandeur peuvent ne pas encore
        # exister aux premières étapes du projet — le tableau de bord reste alors
        # affichable avec des valeurs à zéro.
        from django.utils.dateparse import parse_date

        from apps.demandeurs.models import Demandeur
        from apps.ventes.models import Vente

        # Filtre optionnel par plage de dates (les agrégats, le graphique et les
        # ventes récentes reflètent la période choisie).
        ventes = Vente.objects.all()
        date_debut = parse_date(self.request.GET.get("date_debut", "").strip())
        date_fin = parse_date(self.request.GET.get("date_fin", "").strip())
        if date_debut:
            ventes = ventes.filter(date_vente__gte=date_debut)
        if date_fin:
            ventes = ventes.filter(date_vente__lte=date_fin)
        ctx["filtres"] = {
            "date_debut": self.request.GET.get("date_debut", ""),
            "date_fin": self.request.GET.get("date_fin", ""),
        }

        agregats = ventes.aggregate(
            total=Count("id"),
            quantite=Sum("quantite"),
            chiffre=Sum("prix_total"),
        )

        ctx["total_ventes"] = agregats["total"] or 0
        ctx["quantite_totale"] = agregats["quantite"] or Decimal("0")
        ctx["chiffre_affaires"] = agregats["chiffre"] or Decimal("0")
        ctx["nombre_demandeurs"] = Demandeur.objects.filter(is_active=True).count()

        ctx["ventes_recentes"] = (
            ventes.select_related("demandeur", "utilisateur").order_by("-date_vente", "-id")[:10]
        )

        # Données pour le graphique : chiffre d'affaires des 6 derniers mois.
        ctx["chart"] = self._chiffre_par_mois(ventes)
        return ctx

    @staticmethod
    def _chiffre_par_mois(ventes):
        """Retourne deux listes (labels, valeurs) pour les 6 derniers mois."""
        from django.db.models.functions import TruncMonth

        aujourdhui = timezone.localdate()
        # Premier jour du mois, 5 mois en arrière.
        mois_debut = (aujourdhui.replace(day=1) - timezone.timedelta(days=31 * 5)).replace(day=1)

        par_mois = (
            ventes.filter(date_vente__gte=mois_debut)
            .annotate(mois=TruncMonth("date_vente"))
            .values("mois")
            .annotate(total=Sum("prix_total"))
            .order_by("mois")
        )

        noms_mois = [
            "janv.", "févr.", "mars", "avr.", "mai", "juin",
            "juil.", "août", "sept.", "oct.", "nov.", "déc.",
        ]
        labels, valeurs = [], []
        for ligne in par_mois:
            mois = ligne["mois"]
            labels.append(f"{noms_mois[mois.month - 1]} {mois.year}")
            valeurs.append(float(ligne["total"] or 0))

        return {"labels": labels, "valeurs": valeurs}
