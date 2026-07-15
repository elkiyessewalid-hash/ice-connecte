"""Endpoint JSON de recherche de demandeurs, utilisé par la modale de vente."""
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.views import View

from .models import Demandeur


class DemandeurSearchView(LoginRequiredMixin, View):
    """
    Retourne les demandeurs **actifs** correspondant à la recherche ``q``
    (sur le code ou le libellé). Accessible à tout utilisateur authentifié
    car les trois rôles enregistrent des ventes.
    """

    raise_exception = False  # renvoyer 302 login si non authentifié (cohérent)

    def get(self, request):
        recherche = request.GET.get("q", "").strip()
        qs = Demandeur.objects.filter(is_active=True)
        if recherche:
            qs = qs.filter(Q(code__icontains=recherche) | Q(libelle__icontains=recherche))
        qs = qs.order_by("libelle")[:50]

        resultats = [
            {
                "id": d.pk,
                "code": d.code,
                "libelle": d.libelle,
                "categorie": d.get_categorie_display(),
                "statut": d.get_statut_display(),
            }
            for d in qs
        ]
        return JsonResponse({"results": resultats})
