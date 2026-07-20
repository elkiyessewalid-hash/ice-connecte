"""Tests des ventes : génération du code, calcul, création et exports."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.accounts.models import User
from apps.demandeurs.models import Demandeur, DemandeurPhysique
from apps.referentiel.models import Referentiel

from .models import Vente
from .services import calc_quantite, generate_code_vente, peek_prochain_code


class ServiceTests(TestCase):
    def setUp(self):
        self.ref = Referentiel.objects.create(
            code="8234", nom="Usine", ville="Agadir",
            prix_unitaire=Decimal("4.50"), is_active=True,
        )

    def test_format_code_vente(self):
        date = timezone.datetime(2026, 7, 15).date()
        code = generate_code_vente(self.ref, date)
        self.assertEqual(code, "BG_8234/26 00001")
        # Le second incrémente la séquence.
        self.assertEqual(generate_code_vente(self.ref, date), "BG_8234/26 00002")

    def test_peek_ne_consomme_pas(self):
        date = timezone.datetime(2026, 7, 15).date()
        self.assertEqual(peek_prochain_code(self.ref, date), "BG_8234/26 00001")
        self.assertEqual(peek_prochain_code(self.ref, date), "BG_8234/26 00001")

    def test_numerotation_independante_par_referentiel(self):
        # Chaque référentiel a sa propre séquence annuelle (redémarre à 1).
        ref2 = Referentiel.objects.create(
            code="9000", nom="Usine 2", ville="Rabat",
            prix_unitaire=Decimal("5.00"), is_active=False,
        )
        date = timezone.datetime(2026, 7, 15).date()
        self.assertEqual(generate_code_vente(self.ref, date), "BG_8234/26 00001")
        self.assertEqual(generate_code_vente(self.ref, date), "BG_8234/26 00002")
        # Le second référentiel repart à 1, indépendamment du premier.
        self.assertEqual(generate_code_vente(ref2, date), "BG_9000/26 00001")

    def test_calc_quantite(self):
        self.assertEqual(calc_quantite(Decimal("900"), Decimal("4.50")), Decimal("200.000"))
        self.assertEqual(calc_quantite(Decimal("900"), Decimal("0")), Decimal("0"))


class VenteFlowTests(TestCase):
    def setUp(self):
        self.agent = User.objects.create_user("agent", password="p", role=User.Role.AGENT)
        self.caissier = User.objects.create_user(
            "caissier", password="p", role=User.Role.CAISSIER
        )
        self.ref = Referentiel.objects.create(
            code="8234", nom="Usine", ville="Agadir",
            prix_unitaire=Decimal("4.50"), is_active=True,
        )
        self.demandeur = DemandeurPhysique.objects.create(
            code="DP1", cin="X1", nom="El Amrani", prenom="Youssef",
            statut=Demandeur.Statut.ACHETEUR, is_active=True,
        )

    def test_creation_vente_calcule_quantite_et_code(self):
        # Le caissier est autorisé à saisir une vente.
        self.client.force_login(self.caissier)
        resp = self.client.post(
            reverse("ventes:nouvelle"),
            {"demandeur": self.demandeur.pk, "prix_total": "900", "date_vente": "2026-07-15"},
        )
        self.assertEqual(resp.status_code, 302)
        vente = Vente.objects.latest("id")
        self.assertEqual(vente.code_vente, "BG_8234/26 00001")
        self.assertEqual(vente.quantite, Decimal("200.000"))
        self.assertEqual(vente.prix_unitaire, Decimal("4.50"))
        self.assertEqual(vente.utilisateur, self.caissier)

    def test_agent_ne_peut_pas_creer_vente(self):
        # L'agent est en lecture seule : la saisie lui est interdite (403).
        self.client.force_login(self.agent)
        resp = self.client.post(
            reverse("ventes:nouvelle"),
            {"demandeur": self.demandeur.pk, "prix_total": "900", "date_vente": "2026-07-15"},
        )
        self.assertEqual(resp.status_code, 403)
        self.assertEqual(Vente.objects.count(), 0)

    def test_vente_bloquee_sans_referentiel_actif(self):
        # Sans aucun référentiel, il n'existe aucune source de prix : vente impossible.
        self.ref.delete()
        self.client.force_login(self.caissier)
        self.client.post(
            reverse("ventes:nouvelle"),
            {"demandeur": self.demandeur.pk, "prix_total": "900", "date_vente": "2026-07-15"},
        )
        # Le formulaire est invalide (pas de référentiel actif) -> pas de vente créée.
        self.assertEqual(Vente.objects.count(), 0)

    def test_exports_accessibles(self):
        self.client.force_login(self.agent)
        self.assertEqual(self.client.get(reverse("ventes:export_excel")).status_code, 200)
        self.assertEqual(self.client.get(reverse("ventes:export_pdf")).status_code, 200)

    def test_historique_requiert_connexion(self):
        self.assertEqual(self.client.get(reverse("ventes:historique")).status_code, 302)
