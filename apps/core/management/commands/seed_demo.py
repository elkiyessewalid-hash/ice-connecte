"""
Commande de peuplement de démonstration.

Crée un jeu de données minimal pour tester l'application :
  - un utilisateur par rôle (admin / agent / caissier) ;
  - un référentiel actif ;
  - deux demandeurs (personne physique + personne morale).

Usage :
    python manage.py seed_demo
    python manage.py seed_demo --reset   (recrée les mots de passe des comptes démo)

À NE PAS exécuter en production : ces comptes ont des mots de passe connus.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.demandeurs.models import DemandeurMorale, DemandeurPhysique
from apps.referentiel.models import Referentiel

COMPTES_DEMO = [
    # username, mot de passe, nom, prénom, rôle, superuser
    ("admin", "Admin2026!", "Admin", "Super", User.Role.ADMIN, True),
    ("agent", "Agent2026!", "Agent", "Test", User.Role.AGENT, False),
    ("caissier", "Caissier2026!", "Caissier", "Test", User.Role.CAISSIER, False),
]


class Command(BaseCommand):
    help = "Peuple la base avec un jeu de données de démonstration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Réinitialise les mots de passe des comptes démo.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options["reset"]

        # --- Utilisateurs ---
        for username, mdp, prenom, nom, role, is_super in COMPTES_DEMO:
            user, cree = User.objects.get_or_create(username=username)
            user.first_name = prenom
            user.last_name = nom
            user.role = role
            user.is_staff = is_super
            user.is_superuser = is_super
            if cree or reset:
                user.set_password(mdp)
            user.save()
            etat = "créé" if cree else "mis à jour"
            self.stdout.write(f"  Utilisateur {username} ({role}) {etat}.")

        # --- Référentiel actif ---
        ref, cree = Referentiel.objects.get_or_create(
            code="8234",
            defaults={
                "nom": "Usine à glace Agadir",
                "ville": "Agadir",
                "prix_unitaire": Decimal("4.50"),
                "is_active": True,
            },
        )
        if not ref.is_active:
            ref.is_active = True
            ref.save()
        self.stdout.write(f"  Référentiel {ref.code} {'créé' if cree else 'existant'} et actif.")

        # --- Demandeurs ---
        DemandeurPhysique.objects.get_or_create(
            code="DP-0001",
            defaults={
                "cin": "AB123456",
                "nom": "El Amrani",
                "prenom": "Youssef",
                "statut": DemandeurPhysique.Statut.ACHETEUR,
                "is_active": True,
            },
        )
        DemandeurMorale.objects.get_or_create(
            code="DM-0001",
            defaults={
                "raison_sociale": "Coopérative Al Baraka",
                "nom_representant": "Benali",
                "prenom_representant": "Fatima",
                "cin_representant": "CD654321",
                "statut": DemandeurMorale.Statut.VENDEUR,
                "is_active": True,
            },
        )
        self.stdout.write("  Demandeurs de démonstration prêts.")

        self.stdout.write(self.style.SUCCESS("Jeu de données de démonstration en place."))
        self.stdout.write("Comptes : admin / agent / caissier (voir mots de passe dans seed_demo.py).")
