"""
Contexte de gabarit partagé par toutes les pages.

Expose :
  - ``referentiel_actif`` : le référentiel actif (ou None) — utilisé par la sidebar,
    l'écran de vente et le ticket ;
  - des drapeaux de rôle pratiques pour conditionner l'affichage de la sidebar.

Écrit de façon défensive : si la table n'existe pas encore (avant migration) ou si
l'app référentiel n'est pas prête, on renvoie simplement None sans casser le rendu.
"""
from django.db.utils import Error as DatabaseError


def _get_referentiel_actif():
    try:
        from apps.referentiel.models import Referentiel
    except ImportError:  # app/modèle pas encore disponible
        return None
    try:
        return Referentiel.get_active()
    except DatabaseError:  # table absente (migrations non appliquées)
        return None


def app_context(request):
    user = getattr(request, "user", None)
    is_auth = bool(user and user.is_authenticated)

    return {
        "referentiel_actif": _get_referentiel_actif() if is_auth else None,
        "role_is_admin": is_auth and getattr(user, "is_admin", False),
        "role_is_agent": is_auth and getattr(user, "is_agent", False),
        "role_is_caissier": is_auth and getattr(user, "is_caissier", False),
        "app_name": "Gestion des ventes de blocs de glace",
    }
