from django.db import models
from academique.models import Filiere, Niveau, AnneeAcademique
from inscriptions.models import Inscription
from utilisateurs.models import Caissier


class FraisScolarite(models.Model):
    """Grille tarifaire : montant à payer selon filière + niveau + année"""
    filiere = models.ForeignKey(Filiere, on_delete=models.CASCADE, related_name='frais')
    niveau = models.ForeignKey(Niveau, on_delete=models.CASCADE, related_name='frais')
    annee_academique = models.ForeignKey(AnneeAcademique, on_delete=models.CASCADE, related_name='frais')
    montant_total = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.filiere} - {self.niveau} - {self.annee_academique} : {self.montant_total} FCFA"

    class Meta:
        verbose_name = "Frais de scolarité"
        verbose_name_plural = "Frais de scolarité"
        unique_together = ('filiere', 'niveau', 'annee_academique')


class EcheancePaiement(models.Model):
    """Une échéance prévue dans le calendrier de paiement d'une grille tarifaire"""
    frais_scolarite = models.ForeignKey(
        FraisScolarite,
        on_delete=models.CASCADE,
        related_name='echeances'
    )
    libelle = models.CharField(max_length=50, help_text="Ex: Octobre, Décembre, Mars...")
    montant_attendu = models.DecimalField(max_digits=10, decimal_places=0)
    date_echeance = models.DateField()

    def __str__(self):
        return f"{self.libelle} - {self.montant_attendu} FCFA - {self.date_echeance}"

    class Meta:
        verbose_name = "Échéance de paiement"
        verbose_name_plural = "Échéances de paiement"
        ordering = ['date_echeance']


class Paiement(models.Model):
    """Un versement individuel effectué par un étudiant"""
    MODE_PAIEMENT_CHOICES = (
        ('ESPECES', 'Espèces'),
        ('MOBILE_MONEY', 'Mobile Money'),
        ('VIREMENT', 'Virement bancaire'),
        ('CHEQUE', 'Chèque'),
    )

    inscription = models.ForeignKey(Inscription, on_delete=models.CASCADE, related_name='paiements')
    numero_tranche = models.PositiveSmallIntegerField()
    montant = models.DecimalField(max_digits=10, decimal_places=0)
    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='ESPECES')
    date_paiement = models.DateField()
    enregistre_par = models.ForeignKey(Caissier, on_delete=models.SET_NULL, null=True, related_name='paiements_enregistres')

    def __str__(self):
        return f"{self.inscription.etudiant} - Tranche {self.numero_tranche} - {self.montant} FCFA"

    class Meta:
        verbose_name = "Paiement"
        verbose_name_plural = "Paiements"
        ordering = ['-date_paiement']