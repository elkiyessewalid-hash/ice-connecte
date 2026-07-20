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
