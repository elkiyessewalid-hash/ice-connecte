"""Logique métier du référentiel, isolée des vues."""
from .models import Referentiel


def get_referentiel_actif():
    """Référentiel actif courant (ou None)."""
    return Referentiel.get_active()


def set_actif(referentiel: Referentiel) -> Referentiel:
    """Marque un référentiel comme actif (désactive les autres via son save())."""
    referentiel.is_active = True
    referentiel.save()
    return referentiel
