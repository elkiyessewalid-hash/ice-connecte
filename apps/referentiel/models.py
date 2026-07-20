"""Modèle Référentiel : le catalogue produit (bloc de glace) et son prix unitaire."""
from django.db import models, transaction


class Referentiel(models.Model):
    """
    Un référentiel décrit un point de vente / produit de référence avec son
    prix unitaire (DH/Kg). Règle métier : **un seul référentiel actif** à la fois ;
    c'est son prix unitaire qui alimente automatiquement les nouvelles ventes.
    """

    code = models.CharField("Code", max_length=20, unique=True)
    nom = models.CharField("Nom", max_length=150)
    ville = models.CharField("Ville", max_length=100)
    prix_unitaire = models.DecimalField(
        "Prix unitaire (DH/Kg)", max_digits=10, decimal_places=2
    )
    logo = models.ImageField(
        "Logo", upload_to="referentiels/", blank=True, null=True
    )
    is_active = models.BooleanField("Actif", default=True)

    created_at = models.DateTimeField("Créé le", auto_now_add=True)
    updated_at = models.DateTimeField("Modifié le", auto_now=True)

    class Meta:
        verbose_name = "Référentiel"
        verbose_name_plural = "Référentiels"
        ordering = ["-is_active", "nom"]

    def __str__(self):
        return f"{self.code} — {self.nom}"

    def save(self, *args, **kwargs):
        """
        Garantit qu'il existe toujours **exactement un** référentiel actif :
          - si celui-ci est marqué actif, tous les autres sont désactivés ;
          - s'il est marqué inactif alors qu'aucun autre n'est actif, on le
            réactive (un référentiel doit toujours alimenter les ventes en prix).
        Le tout dans une seule transaction.
        """
        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.is_active:
                Referentiel.objects.exclude(pk=self.pk).filter(is_active=True).update(
                    is_active=False
                )
            elif not Referentiel.objects.filter(is_active=True).exists():
                Referentiel.objects.filter(pk=self.pk).update(is_active=True)
                self.is_active = True

    @classmethod
    def get_active(cls):
        """Retourne le référentiel actif, ou None s'il n'y en a aucun."""
        return cls.objects.filter(is_active=True).first()
