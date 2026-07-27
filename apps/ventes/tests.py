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

    def test_safe_txt_neutralise_formule_excel(self):
        from apps.ventes.exports import _safe_txt
        self.assertEqual(_safe_txt("=SUM(A1:A9)"), "'=SUM(A1:A9)")
        self.assertEqual(_safe_txt("+1+1"), "'+1+1")
        self.assertEqual(_safe_txt("@cmd"), "'@cmd")
        self.assertEqual(_safe_txt("BG_8234/26 00001"), "BG_8234/26 00001")
        self.assertEqual(_safe_txt("Coopérative Al Baraka"), "Coopérative Al Baraka")


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

    def test_creation_vente_par_quantite(self):
        # Saisie « quantité d'abord » : le prix total est calculé (qté × prix unitaire).
        self.client.force_login(self.caissier)
        resp = self.client.post(
            reverse("ventes:nouvelle"),
            {
                "demandeur": self.demandeur.pk, "quantite": "200",
                "saisie": "quantite", "date_vente": "2026-07-15",
            },
        )
        self.assertEqual(resp.status_code, 302)
        vente = Vente.objects.latest("id")
        self.assertEqual(vente.quantite, Decimal("200.000"))
        self.assertEqual(vente.prix_total, Decimal("900.00"))  # 200 × 4,50
        self.assertEqual(vente.prix_unitaire, Decimal("4.50"))

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

    def test_montant_hors_limites_refuse(self):
        # Un montant démesuré est refusé proprement (pas d'erreur DB / 500).
        self.client.force_login(self.caissier)
        resp = self.client.post(
            reverse("ventes:nouvelle"),
            {"demandeur": self.demandeur.pk, "prix_total": "1000000000000", "date_vente": "2026-07-15"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Vente.objects.count(), 0)

    def test_date_vente_future_refusee(self):
        from datetime import timedelta
        self.client.force_login(self.caissier)
        future = (timezone.localdate() + timedelta(days=5)).isoformat()
        resp = self.client.post(
            reverse("ventes:nouvelle"),
            {"demandeur": self.demandeur.pk, "prix_total": "900", "date_vente": future},
        )
        self.assertEqual(resp.status_code, 200)  # réaffiche le formulaire invalide
        self.assertEqual(Vente.objects.count(), 0)

    def test_exports_reserves_admin_caissier(self):
        # Le caissier peut exporter ; l'agent (lecture seule) est refusé (403).
        self.client.force_login(self.caissier)
        self.assertEqual(self.client.get(reverse("ventes:export_excel")).status_code, 200)
        self.assertEqual(self.client.get(reverse("ventes:export_pdf")).status_code, 200)
        self.client.force_login(self.agent)
        self.assertEqual(self.client.get(reverse("ventes:export_excel")).status_code, 403)
        self.assertEqual(self.client.get(reverse("ventes:export_pdf")).status_code, 403)

    def test_historique_requiert_connexion(self):
        self.assertEqual(self.client.get(reverse("ventes:historique")).status_code, 302)


class HistoriqueListeTests(TestCase):
    def setUp(self):
        self.caissier = User.objects.create_user(
            "caissier", password="p", role=User.Role.CAISSIER
        )
        self.ref = Referentiel.objects.create(
            code="8234", nom="Usine", ville="Agadir",
            prix_unitaire=Decimal("4.50"), is_active=True,
        )
        self.dem = DemandeurPhysique.objects.create(
            code="DP1", cin="X1", nom="El Amrani", prenom="Youssef",
            statut=Demandeur.Statut.ACHETEUR, is_active=True,
        )
        for i in range(6):
            v = Vente(
                demandeur=self.dem, referentiel=self.ref,
                prix_unitaire=self.ref.prix_unitaire, quantite=Decimal("10"),
                prix_total=Decimal(100 * (i + 1)),
            )
            v.utilisateur = self.caissier
            v.save()
        self.client.force_login(self.caissier)

    def test_pagination_5_par_page(self):
        resp = self.client.get(reverse("ventes:historique"))
        self.assertEqual(len(resp.context["ventes"]), 5)
        self.assertTrue(resp.context["is_paginated"])

    def test_filtre_montant(self):
        # Montants 100..600 ; [300, 500] -> 300, 400, 500 = 3 ventes.
        resp = self.client.get(
            reverse("ventes:historique"), {"montant_min": "300", "montant_max": "500"}
        )
        self.assertEqual(resp.context["paginator"].count, 3)

    def test_montant_invalide_est_ignore(self):
        resp = self.client.get(reverse("ventes:historique"), {"montant_min": "abc"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["paginator"].count, 6)

    def test_filtres_invalides_ne_plantent_pas(self):
        # Date illisible + montants négatifs : ignorés, aucun 500.
        resp = self.client.get(
            reverse("ventes:historique"),
            {"date_debut": "pas-une-date", "montant_min": "-5", "montant_max": "xyz"},
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context["paginator"].count, 6)

    def test_montant_intervalle_inverse_corrige(self):
        # min=500, max=300 -> corrigé en 300..500 -> 300, 400, 500 = 3 ventes.
        resp = self.client.get(
            reverse("ventes:historique"), {"montant_min": "500", "montant_max": "300"}
        )
        self.assertEqual(resp.context["paginator"].count, 3)

    def test_htmx_renvoie_fragment(self):
        resp = self.client.get(reverse("ventes:historique"), HTTP_HX_REQUEST="true")
        self.assertNotContains(resp, "<html")
        self.assertContains(resp, "<table")

    def test_ticket_detail(self):
        v = Vente.objects.first()
        resp = self.client.get(reverse("ventes:ticket_detail", args=[v.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, v.code_vente)

    def test_ticket_page_deux_exemplaires(self):
        # Le ticket imprimable présente deux exemplaires sur une page A4.
        v = Vente.objects.first()
        resp = self.client.get(reverse("ventes:ticket", args=[v.pk]))
        self.assertContains(resp, "ticket-sheet")
        # Deux cartes ticket (deux exemplaires) sur la même page.
        self.assertContains(resp, 'class="ticket-title"', count=2)
        self.assertContains(resp, "Exemplaire 1")
        self.assertContains(resp, "Exemplaire 2")
