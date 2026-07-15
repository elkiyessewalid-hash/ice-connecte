"""
Logique métier des ventes : génération du code de vente et calculs.

Format du code (décision D2) :
    BG_<code_référentiel>/<AA> <NNNNN>
Exemple :
    BG_8234/26 00001
où AA = 2 derniers chiffres de l'année et NNNNN = séquence à 5 chiffres,
incrémentée par année.
"""
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from django.db import transaction
from django.utils import timezone

from .models import SequenceCounter

CENT = Decimal("0.01")
MILLI = Decimal("0.001")


def generate_code_vente(referentiel, date_vente=None) -> str:
    """
    Génère un code de vente unique et croissant pour l'année de ``date_vente``.
    Le compteur est verrouillé (select_for_update) pour être sûr en concurrence.
    """
    date_vente = date_vente or timezone.localdate()
    annee = date_vente.year

    with transaction.atomic():
        compteur, _ = SequenceCounter.objects.select_for_update().get_or_create(annee=annee)
        compteur.dernier_numero += 1
        compteur.save(update_fields=["dernier_numero"])
        numero = compteur.dernier_numero

    code_ref = referentiel.code if referentiel else "----"
    aa = f"{annee % 100:02d}"
    return f"BG_{code_ref}/{aa} {numero:05d}"


def peek_prochain_code(referentiel, date_vente=None) -> str:
    """
    Aperçu (non consommant) du prochain code, pour affichage sur le formulaire.
    Ne réserve pas le numéro : la valeur définitive est fixée à l'enregistrement.
    """
    date_vente = date_vente or timezone.localdate()
    annee = date_vente.year
    compteur = SequenceCounter.objects.filter(annee=annee).first()
    prochain = (compteur.dernier_numero if compteur else 0) + 1
    code_ref = referentiel.code if referentiel else "----"
    aa = f"{annee % 100:02d}"
    return f"BG_{code_ref}/{aa} {prochain:05d}"


def _to_decimal(valeur) -> Decimal:
    try:
        return Decimal(str(valeur))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def calc_quantite(prix_total, prix_unitaire) -> Decimal:
    """Qté (Kg) = Prix total / Prix unitaire (décision D1)."""
    pu = _to_decimal(prix_unitaire)
    if pu == 0:
        return Decimal("0")
    return (_to_decimal(prix_total) / pu).quantize(MILLI, rounding=ROUND_HALF_UP)


def calc_prix_total(quantite, prix_unitaire) -> Decimal:
    """Prix total (DH) = Qté × Prix unitaire (sens inverse, pratique/bonus)."""
    return (_to_decimal(quantite) * _to_decimal(prix_unitaire)).quantize(
        CENT, rounding=ROUND_HALF_UP
    )
