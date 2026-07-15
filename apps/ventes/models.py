"""Modèles du cœur métier : Vente et compteur de séquence des codes de vente."""
from django.conf import settings
from django.db import models
from django.utils import timezone


class SequenceCounter(models.Model):
    """
    Compteur de séquence par année, garantissant un numéro de vente unique et
    croissant même en cas d'accès concurrents (verrouillage via select_for_update
    dans le service de génération de code).
    """

    annee = models.PositiveIntegerField("Année", unique=True)
    dernier_numero = models.PositiveIntegerField("Dernier numéro", default=0)

    class Meta:
        verbose_name = "Compteur de séquence"
        verbose_name_plural = "Compteurs de séquence"

    def __str__(self):
        return f"{self.annee} → {self.dernier_numero}"


class Vente(models.Model):
    """
    Une vente de blocs de glace.

    Le prix unitaire et le référentiel sont figés (snapshot) au moment de la vente
    pour préserver l'historique même si le référentiel actif change ensuite.
    """

    code_vente = models.CharField(
        "Code vente", max_length=40, unique=True, editable=False
    )
    demandeur = models.ForeignKey(
        "demandeurs.Demandeur",
        on_delete=models.PROTECT,
        related_name="ventes",
        verbose_name="Demandeur",
    )
    referentiel = models.ForeignKey(
        "referentiel.Referentiel",
        on_delete=models.PROTECT,
        related_name="ventes",
        verbose_name="Référentiel",
    )
    prix_unitaire = models.DecimalField(
        "Prix unitaire (DH/Kg)", max_digits=10, decimal_places=2
    )
    quantite = models.DecimalField("Quantité (Kg)", max_digits=12, decimal_places=3)
    prix_total = models.DecimalField("Prix total (DH)", max_digits=14, decimal_places=2)
    date_vente = models.DateField("Date de vente", default=timezone.localdate)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="ventes",
        verbose_name="Utilisateur",
    )
    created_at = models.DateTimeField("Enregistrée le", auto_now_add=True)

    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ["-date_vente", "-id"]

    def __str__(self):
        return self.code_vente

    def save(self, *args, **kwargs):
        # Attribue le code de vente définitif au premier enregistrement.
        if not self.code_vente:
            from .services import generate_code_vente

            self.code_vente = generate_code_vente(self.referentiel, self.date_vente)
        super().save(*args, **kwargs)
