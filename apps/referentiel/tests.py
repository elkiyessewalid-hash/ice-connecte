"""Tests du référentiel : règle « un seul actif »."""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User

from .models import Referentiel


class ReferentielActifTests(TestCase):
    def test_un_seul_referentiel_actif(self):
        r1 = Referentiel.objects.create(
            code="A1", nom="Un", ville="Agadir", prix_unitaire=Decimal("4.50"), is_active=True
        )
        r2 = Referentiel.objects.create(
            code="A2", nom="Deux", ville="Safi", prix_unitaire=Decimal("5.00"), is_active=True
        )
        r1.refresh_from_db()
        r2.refresh_from_db()
        # L'activation du second désactive le premier.
        self.assertFalse(r1.is_active)
        self.assertTrue(r2.is_active)
        self.assertEqual(Referentiel.objects.filter(is_active=True).count(), 1)

    def test_get_active(self):
        self.assertIsNone(Referentiel.get_active())
        r = Referentiel.objects.create(
            code="A1", nom="Un", ville="Agadir", prix_unitaire=Decimal("4.50"), is_active=True
        )
        self.assertEqual(Referentiel.get_active(), r)

    def test_reactivation_si_unique_desactive(self):
        # Un référentiel unique désactivé par erreur est automatiquement réactivé.
        r = Referentiel.objects.create(
            code="A1", nom="Un", ville="Agadir", prix_unitaire=Decimal("4.50"), is_active=True
        )
        r.is_active = False
        r.save()
        r.refresh_from_db()
        self.assertTrue(r.is_active)

    def test_contrainte_db_un_seul_actif(self):
        # La contrainte DB rejette deux référentiels actifs (même en contournant save()).
        from django.db import IntegrityError, transaction
        Referentiel.objects.create(
            code="A1", nom="Un", ville="Agadir", prix_unitaire=Decimal("4.50"), is_active=True
        )
        r2 = Referentiel.objects.create(
            code="A2", nom="Deux", ville="Safi", prix_unitaire=Decimal("5.00"), is_active=False
        )
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Referentiel.objects.filter(pk=r2.pk).update(is_active=True)


class ReferentielSingletonViewTests(TestCase):
    """Règle métier : un seul référentiel, toujours actif (côté vues)."""

    def setUp(self):
        self.admin = User.objects.create_user("admin", password="p", role=User.Role.ADMIN)
        self.client.force_login(self.admin)

    def test_creation_bloquee_si_referentiel_existe(self):
        existant = Referentiel.objects.create(
            code="A1", nom="Un", ville="Agadir", prix_unitaire=Decimal("4.50")
        )
        resp = self.client.get(reverse("referentiel:create"))
        # Redirigé vers la modification de l'existant : pas de second référentiel.
        self.assertRedirects(resp, reverse("referentiel:update", args=[existant.pk]))
        self.assertEqual(Referentiel.objects.count(), 1)

    def test_referentiel_cree_est_toujours_actif(self):
        # Même si is_active=False est soumis, le référentiel unique est forcé actif.
        self.client.post(
            reverse("referentiel:create"),
            {
                "code": "A1", "nom": "Un", "ville": "Agadir",
                "prix_unitaire": "4.50", "is_active": False,
            },
        )
        self.assertEqual(Referentiel.objects.count(), 1)
        self.assertTrue(Referentiel.objects.first().is_active)
