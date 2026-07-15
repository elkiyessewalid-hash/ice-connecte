"""Tests des demandeurs : libellé/catégorie automatiques + API de recherche."""
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User

from .models import Demandeur, DemandeurMorale, DemandeurPhysique


class DemandeurModelTests(TestCase):
    def test_physique_libelle_et_categorie_auto(self):
        d = DemandeurPhysique.objects.create(
            code="DP1", cin="X1", nom="El Amrani", prenom="Youssef",
            statut=Demandeur.Statut.ACHETEUR,
        )
        self.assertEqual(d.categorie, Demandeur.Categorie.PHYSIQUE)
        self.assertEqual(d.libelle, "El Amrani Youssef")

    def test_morale_libelle_et_categorie_auto(self):
        d = DemandeurMorale.objects.create(
            code="DM1", raison_sociale="Coop Baraka", nom_representant="Benali",
            prenom_representant="Fatima", cin_representant="Y2",
            statut=Demandeur.Statut.VENDEUR,
        )
        self.assertEqual(d.categorie, Demandeur.Categorie.MORALE)
        self.assertEqual(d.libelle, "Coop Baraka")


class DemandeurSearchApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("agent", password="p", role=User.Role.AGENT)
        DemandeurPhysique.objects.create(
            code="DP1", cin="X1", nom="El Amrani", prenom="Youssef",
            statut=Demandeur.Statut.ACHETEUR, is_active=True,
        )
        DemandeurPhysique.objects.create(
            code="DP2", cin="X2", nom="Inactif", prenom="Test",
            statut=Demandeur.Statut.ACHETEUR, is_active=False,
        )

    def test_recherche_exclut_inactifs(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("demandeurs:search"))
        data = resp.json()
        codes = [d["code"] for d in data["results"]]
        self.assertIn("DP1", codes)
        self.assertNotIn("DP2", codes)

    def test_recherche_par_nom(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("demandeurs:search"), {"q": "Amrani"})
        self.assertEqual(len(resp.json()["results"]), 1)

    def test_recherche_exige_authentification(self):
        resp = self.client.get(reverse("demandeurs:search"))
        self.assertEqual(resp.status_code, 302)  # redirigé vers login
