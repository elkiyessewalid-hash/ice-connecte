"""Tests du référentiel : règle « un seul actif »."""
from decimal import Decimal

from django.test import TestCase

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
