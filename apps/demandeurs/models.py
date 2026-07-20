"""
Modèles Demandeurs.

On utilise l'héritage multi-table : une base concrète ``Demandeur`` porte les
champs communs (code, statut, catégorie, actif, libellé d'affichage), et deux
sous-classes ``DemandeurPhysique`` / ``DemandeurMorale`` ajoutent leurs champs
spécifiques. Une vente référence un unique ``Demandeur`` (FK propre), et la
recherche/affichage s'appuie sur la table de base.
"""
from django.db import models


class Demandeur(models.Model):
    """Base commune aux personnes physiques et morales."""

    class Statut(models.TextChoices):
        ACHETEUR = "ACHETEUR", "Acheteur"
        VENDEUR = "VENDEUR", "Vendeur"

    class Categorie(models.TextChoices):
        PHYSIQUE = "PHYSIQUE", "Personne physique"
        MORALE = "MORALE", "Personne morale"

    code = models.CharField("Code", max_length=10, unique=True)
    statut = models.CharField("Statut", max_length=10, choices=Statut.choices)
    categorie = models.CharField("Catégorie", max_length=10, choices=Categorie.choices)
    # Libellé lisible, recalculé depuis le sous-type à chaque enregistrement.
    # Permet des listes / recherches / exports sans jointure vers les sous-tables.
    libelle = models.CharField("Libellé", max_length=255, blank=True)
    is_active = models.BooleanField("Actif", default=True)

    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        verbose_name = "Demandeur"
        verbose_name_plural = "Demandeurs"
        ordering = ["libelle", "code"]

    def __str__(self):
        return f"{self.code} — {self.libelle}" if self.libelle else self.code

    def compute_libelle(self) -> str:
        """Libellé par défaut (surchargé par les sous-classes)."""
        return self.libelle or self.code


class DemandeurPhysique(Demandeur):
    """Personne physique : CIN, Nom, Prénom."""

    cin = models.CharField("CIN", max_length=20, unique=True)
    nom = models.CharField("Nom", max_length=100)
    prenom = models.CharField("Prénom", max_length=100)

    class Meta:
        verbose_name = "Demandeur — personne physique"
        verbose_name_plural = "Demandeurs — personnes physiques"

    def compute_libelle(self) -> str:
        return f"{self.nom} {self.prenom}".strip()

    def save(self, *args, **kwargs):
        self.categorie = Demandeur.Categorie.PHYSIQUE
        self.libelle = self.compute_libelle()
        super().save(*args, **kwargs)


class DemandeurMorale(Demandeur):
    """Personne morale : Raison sociale + représentant."""

    raison_sociale = models.CharField("Raison sociale", max_length=200)
    nom_representant = models.CharField("Nom du représentant", max_length=100)
    prenom_representant = models.CharField("Prénom du représentant", max_length=100)
    cin_representant = models.CharField("CIN du représentant", max_length=20)

    class Meta:
        verbose_name = "Demandeur — personne morale"
        verbose_name_plural = "Demandeurs — personnes morales"

    def compute_libelle(self) -> str:
        return self.raison_sociale.strip()

    def save(self, *args, **kwargs):
        self.categorie = Demandeur.Categorie.MORALE
        self.libelle = self.compute_libelle()
        super().save(*args, **kwargs)
