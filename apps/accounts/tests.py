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

    def test_login_page_a_le_toggle_mot_de_passe(self):
        resp = self.client.get(reverse("accounts:login"))
        self.assertContains(resp, "toggleReady")

    def test_verrouillage_apres_echecs_repetes(self):
        # django-axes : 5 échecs verrouillent ; la 6e tentative (même correcte) est refusée.
        for _ in range(5):
            self.client.post(
                reverse("accounts:login"), {"username": "admin", "password": "faux"}
            )
        resp = self.client.post(
            reverse("accounts:login"), {"username": "admin", "password": "Admin2026!"}
        )
        self.assertEqual(resp.status_code, 403)


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

    def test_admin_ne_peut_pas_se_supprimer(self):
        self.client.force_login(self.admin)
        resp = self.client.post(reverse("accounts:user_delete", args=[self.admin.pk]))
        self.assertRedirects(resp, reverse("accounts:user_list"))
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

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


class UserListFilterTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user("admin", password="p", role=User.Role.ADMIN)
        for i in range(6):
            User.objects.create_user(
                f"agent{i}", password="p", role=User.Role.AGENT,
                last_name="Dupont", first_name=f"A{i}",
            )
        User.objects.create_user(
            "cordi", password="p", role=User.Role.CAISSIER,
            last_name="Zahra", first_name="Nour",
        )
        self.client.force_login(self.admin)

    def test_pagination_5_par_page(self):
        resp = self.client.get(reverse("accounts:user_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context["is_paginated"])
        self.assertEqual(len(resp.context["utilisateurs"]), 5)

    def test_filtre_par_role(self):
        resp = self.client.get(reverse("accounts:user_list"), {"role": User.Role.CAISSIER})
        self.assertEqual(resp.context["paginator"].count, 1)

    def test_filtre_par_etat(self):
        User.objects.filter(username="agent0").update(is_active=False)
        resp = self.client.get(reverse("accounts:user_list"), {"etat": "inactif"})
        self.assertEqual(resp.context["paginator"].count, 1)

    def test_recherche_par_nom(self):
        resp = self.client.get(reverse("accounts:user_list"), {"q": "Zahra"})
        self.assertEqual(resp.context["paginator"].count, 1)

    def test_htmx_renvoie_fragment(self):
        resp = self.client.get(reverse("accounts:user_list"), HTTP_HX_REQUEST="true")
        self.assertNotContains(resp, "<html")
        self.assertContains(resp, "<table")

    def test_detail_utilisateur(self):
        resp = self.client.get(reverse("accounts:user_detail", args=[self.admin.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "admin")


class UserFieldConstraintTests(TestCase):
    """Longueurs maximales : login 30, nom/prénom 25, mot de passe 20."""

    def _data(self, **over):
        data = {
            "username": "u1", "last_name": "Nom", "first_name": "Prenom",
            "role": User.Role.CAISSIER, "is_active": True,
            "password1": "MotDePasse2026!", "password2": "MotDePasse2026!",
        }
        data.update(over)
        return data

    def test_login_max_30(self):
        from apps.accounts.forms import UserCreateForm
        f = UserCreateForm(data=self._data(username="a" * 31))
        self.assertFalse(f.is_valid())
        self.assertIn("username", f.errors)

    def test_nom_max_25(self):
        from apps.accounts.forms import UserCreateForm
        f = UserCreateForm(data=self._data(last_name="N" * 26))
        self.assertFalse(f.is_valid())
        self.assertIn("last_name", f.errors)

    def test_password_max_20(self):
        from apps.accounts.forms import UserCreateForm
        pw = "Ab1!" + "x" * 20  # 24 caractères
        f = UserCreateForm(data=self._data(password1=pw, password2=pw))
        self.assertFalse(f.is_valid())
        self.assertIn("password1", f.errors)

    def test_valeurs_valides(self):
        from apps.accounts.forms import UserCreateForm
        f = UserCreateForm(data=self._data())
        self.assertTrue(f.is_valid(), f.errors)
