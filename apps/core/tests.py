"""Tests du tableau de bord (accessible à tous les rôles authentifiés)."""
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user("agent", password="p", role=User.Role.AGENT)
        self.caissier = User.objects.create_user(
            "caissier", password="p", role=User.Role.CAISSIER
        )

    def test_agent_accede_au_tableau_de_bord(self):
        self.client.force_login(self.agent)
        resp = self.client.get(reverse("core:dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_caissier_accede_au_tableau_de_bord(self):
        self.client.force_login(self.caissier)
        resp = self.client.get(reverse("core:dashboard"))
        self.assertEqual(resp.status_code, 200)

    def test_lien_tableau_de_bord_visible_pour_agent(self):
        # Le lien de retour au tableau de bord doit figurer dans la barre latérale.
        self.client.force_login(self.agent)
        resp = self.client.get(reverse("ventes:historique"))
        self.assertContains(resp, "Tableau de bord")
        self.assertContains(resp, reverse("core:dashboard"))

    def test_dashboard_requiert_connexion(self):
        resp = self.client.get(reverse("core:dashboard"))
        self.assertEqual(resp.status_code, 302)

    def test_dashboard_filtre_par_date(self):
        from datetime import date
        from decimal import Decimal

        from apps.demandeurs.models import Demandeur, DemandeurPhysique
        from apps.referentiel.models import Referentiel
        from apps.ventes.models import Vente

        ref = Referentiel.objects.create(
            code="R1", nom="N", ville="V", prix_unitaire=Decimal("4.50"), is_active=True
        )
        dem = DemandeurPhysique.objects.create(
            code="D1", cin="C1", nom="A", prenom="B", statut=Demandeur.Statut.ACHETEUR
        )
        for jour in (date(2026, 1, 1), date(2026, 7, 1)):
            v = Vente(
                demandeur=dem, referentiel=ref, prix_unitaire=ref.prix_unitaire,
                quantite=Decimal("10"), prix_total=Decimal("45"), date_vente=jour,
            )
            v.utilisateur = self.agent
            v.save()
        self.client.force_login(self.agent)
        resp = self.client.get(reverse("core:dashboard"), {"date_debut": "2026-06-01"})
        self.assertEqual(resp.context["total_ventes"], 1)  # seule la vente de juillet
