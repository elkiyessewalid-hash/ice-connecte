"""Filtres de formatage de nombres (notation compacte : 1,2 K, 3 M…)."""
from django import template

register = template.Library()

_PALIERS = ((1_000_000_000, "Md"), (1_000_000, "M"), (1_000, "K"))


@register.filter
def compact(value):
    """
    Notation compacte d'un nombre : 745 -> « 745 », 744962 -> « 745 K »,
    1250000 -> « 1,3 M ». Séparateur décimal français (virgule).
    Réservé aux résumés (KPI) ; les montants exacts gardent leur affichage.
    """
    try:
        nombre = float(value)
    except (TypeError, ValueError):
        return value

    signe = "-" if nombre < 0 else ""
    nombre = abs(nombre)

    for seuil, suffixe in _PALIERS:
        if nombre >= seuil:
            reduit = nombre / seuil
            # 1 décimale sous 10 (ex. 1,3 M), entier au-delà (ex. 745 K).
            texte = f"{reduit:.1f}" if reduit < 10 else f"{reduit:.0f}"
            texte = texte.rstrip("0").rstrip(".")
            return f"{signe}{texte} {suffixe}".replace(".", ",")

    # Sous 1000 : entier si rond, sinon 2 décimales.
    texte = f"{nombre:.0f}" if nombre == int(nombre) else f"{nombre:.2f}"
    return f"{signe}{texte}".replace(".", ",")
