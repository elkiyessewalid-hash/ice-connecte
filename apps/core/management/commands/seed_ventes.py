"""
Peuplement de nombreuses ventes de démonstration, avec **dates variées** (réparties
sur plusieurs mois) et **montants aléatoires** — pour tester le tableau de bord,
le graphique, l'historique (pagination, filtres, montants) et l'historique par demandeur.

Usage :
    python manage.py seed_ventes                 # 250 ventes sur ~14 mois
    python manage.py seed_ventes --count 500 --days 730
    python manage.py seed_ventes --clear         # vide d'abord les ventes existantes

À NE PAS exécuter en production.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.demandeurs.models import Demandeur, DemandeurMorale, DemandeurPhysique
from apps.referentiel.models import Referentiel
from apps.ventes.models import Vente
from apps.ventes.services import calc_quantite

NOMS = ["El Amrani", "Benali", "Alaoui", "Tazi", "Bennani", "Chraibi", "Idrissi", "Fassi"]
PRENOMS = ["Youssef", "Fatima", "Mohamed", "Salma", "Karim", "Nadia", "Omar", "Imane"]
SOCIETES = [
    "Coopérative Al Baraka", "Pêcheries du Sud", "Glace Atlas", "Marée Fraîche",
    "Comptoir Océan", "Souss Distribution", "Anfa Négoce", "Rif Poissons",
]
CENTIMES = ["0.00", "0.25", "0.50", "0.75"]


class Command(BaseCommand):
    help = "Crée de nombreuses ventes de démonstration (dates variées, montants aléatoires)."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=250, help="Nombre de ventes à créer.")
        parser.add_argument("--days", type=int, default=420, help="Étalement des dates sur N jours dans le passé.")
        parser.add_argument("--clear", action="store_true", help="Supprime les ventes existantes d'abord.")
        parser.add_argument("--seed", type=int, default=None, help="Graine aléatoire (résultats reproductibles).")

    def handle(self, *args, **opts):
        if opts["seed"] is not None:
            random.seed(opts["seed"])

        referentiel = self._referentiel()
        vendeurs = self._vendeurs()
        demandeurs = self._demandeurs()

        if opts["clear"]:
            supprimees = Vente.objects.count()
            Vente.objects.all().delete()
            self.stdout.write(f"  {supprimees} ventes supprimées.")

        pu = referentiel.prix_unitaire
        aujourdhui = timezone.localdate()
        count, days = opts["count"], opts["days"]

        cree = 0
        with transaction.atomic():
            for _ in range(count):
                jour = aujourdhui - timedelta(days=random.randint(0, days))
                prix_total = Decimal(random.randint(45, 5000)) + Decimal(random.choice(CENTIMES))
                vente = Vente(
                    demandeur=random.choice(demandeurs),
                    referentiel=referentiel,
                    prix_unitaire=pu,
                    quantite=calc_quantite(prix_total, pu),
                    prix_total=prix_total,
                    date_vente=jour,
                    utilisateur=random.choice(vendeurs),
                )
                vente.save()  # génère le code_vente
                cree += 1

        total = Vente.objects.count()
        plage = f"{aujourdhui - timedelta(days=days):%d/%m/%Y} → {aujourdhui:%d/%m/%Y}"
        self.stdout.write(self.style.SUCCESS(f"{cree} ventes créées (dates {plage}). Total en base : {total}."))

    # ------------------------------------------------------------------ helpers
    def _referentiel(self):
        ref = Referentiel.get_active()
        if ref is None:
            ref, _ = Referentiel.objects.get_or_create(
                code="8234",
                defaults={
                    "nom": "Usine à glace Agadir", "ville": "Agadir",
                    "prix_unitaire": Decimal("4.50"), "is_active": True,
                },
            )
            self.stdout.write(f"  Référentiel {ref.code} prêt et actif.")
        return ref

    def _vendeurs(self):
        vendeurs = list(User.objects.filter(role__in=[User.Role.ADMIN, User.Role.CAISSIER]))
        if not vendeurs:
            vendeurs = [User.objects.create_user(
                "caissier", password="Caissier2026!", role=User.Role.CAISSIER,
                first_name="Caissier", last_name="Démo",
            )]
            self.stdout.write("  Compte caissier de démo créé.")
        return vendeurs

    def _demandeurs(self):
        """Réutilise les demandeurs actifs ; en crée un petit lot varié si besoin."""
        for i in range(1, 7):
            DemandeurPhysique.objects.get_or_create(
                code=f"SP-{i:03d}",
                defaults={
                    "cin": f"SEEDP{i:04d}",
                    "nom": random.choice(NOMS), "prenom": random.choice(PRENOMS),
                    "statut": random.choice(Demandeur.Statut.values),
                    "is_active": True,
                },
            )
        for i in range(1, 5):
            DemandeurMorale.objects.get_or_create(
                code=f"SM-{i:03d}",
                defaults={
                    "raison_sociale": SOCIETES[(i - 1) % len(SOCIETES)],
                    "nom_representant": random.choice(NOMS),
                    "prenom_representant": random.choice(PRENOMS),
                    "cin_representant": f"SEEDM{i:04d}",
                    "statut": random.choice(Demandeur.Statut.values),
                    "is_active": True,
                },
            )
        demandeurs = list(Demandeur.objects.filter(is_active=True))
        self.stdout.write(f"  {len(demandeurs)} demandeurs actifs disponibles.")
        return demandeurs
