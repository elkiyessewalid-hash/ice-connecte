"""Tests de l'authentification et de la gestion des utilisateurs."""
from django.test import TestCase
from django.urls import reverse

from .models import User


class AuthenticationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            "admin", password="Admin2026!", role=User.Role.ADMIN
        )
        self.agent = User.objects.create_user(
            "agent", password="Agent2026!", role=User.Role.AGENT
        )
        self.caissier = User.objects.create_user(
            "caissier", password="Caissier2026!", role=User.Role.CAISSIER
        )

    def test_mot_de_passe_hache(self):
        """Le mot de passe ne doit jamais être stocké en clair."""
        self.assertNotEqual(self.admin.password, "Admin2026!")
        self.assertTrue(self.admin.check_password("Admin2026!"))

    def test_login_redirige_admin_vers_dashboard(self):
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "admin", "password": "Admin2026!"},
        )
        self.assertRedirects(resp, reverse("core:dashboard"))

    def test_login_redirige_agent_vers_historique(self):
        # L'agent est en lecture seule : il arrive sur l'historique, pas la saisie.
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "agent", "password": "Agent2026!"},
        )
        self.assertRedirects(resp, reverse("ventes:historique"))

    def test_login_redirige_caissier_vers_nouvelle_vente(self):
        # Le caissier peut créer des ventes : il arrive sur la saisie.
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "caissier", "password": "Caissier2026!"},
        )
        self.assertRedirects(resp, reverse("ventes:nouvelle"))

    def test_login_invalide(self):
        resp = self.client.post(
            reverse("accounts:login"),
            {"username": "admin", "password": "faux"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "incorrect")


class UserManagementPermissionTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", password="p", role=User.Role.ADMIN)
        self.agent = User.objects.create_user("agent", password="p", role=User.Role.AGENT)

    def test_admin_accede_a_la_liste(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse("accounts:user_list")).status_code, 200)

    def test_agent_interdit(self):
        self.client.force_login(self.agent)
        self.assertEqual(self.client.get(reverse("accounts:user_list")).status_code, 403)

    def test_creation_utilisateur(self):
        self.client.force_login(self.admin)
        resp = self.client.post(
            reverse("accounts:user_create"),
            {
                "username": "caissier1",
                "last_name": "Test",
                "first_name": "Caissier",
                "role": User.Role.CAISSIER,
                "is_active": True,
                "password1": "MotDePasse2026!",
                "password2": "MotDePasse2026!",
            },
        )
        self.assertRedirects(resp, reverse("accounts:user_list"))
        u = User.objects.get(username="caissier1")
        self.assertTrue(u.check_password("MotDePasse2026!"))
        self.assertEqual(u.role, User.Role.CAISSIER)
