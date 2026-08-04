from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from academique.models import Filiere, Niveau, AnneeAcademique
from utilisateurs.models import Etudiant

validateur_telephone = RegexValidator(
    regex=r'^\d{8}$',
    message="Le numéro de téléphone doit contenir exactement 8 chiffres (ex: 70123456)."
)


class Inscription(models.Model):
    STATUT_CHOICES = (
        ('EN_ATTENTE', 'En attente'),
        ('VALIDEE', 'Validée'),
        ('REJETEE', 'Rejetée'),
    )

    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    niveau = models.ForeignKey(
        Niveau,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    annee_academique = models.ForeignKey(
        AnneeAcademique,
        on_delete=models.CASCADE,
        related_name='inscriptions'
    )
    telephone_inscription = models.CharField(
        max_length=8,
        verbose_name="Numéro de téléphone utilisé pour l'inscription",
        help_text="8 chiffres, sert d'identifiant unique pour le caissier (évite les confusions entre homonymes)",
        validators=[validateur_telephone],
        blank=True,
        null=True
    )
    remise = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        default=0,
        verbose_name="Remise accordée (FCFA)",
        help_text="Réduction individuelle sur les frais de scolarité de cet étudiant (bourse, geste commercial...)"
    )
    date_inscription = models.DateField(auto_now_add=True)
    statut = models.CharField(
        max_length=15,
        choices=STATUT_CHOICES,
        default='EN_ATTENTE'
    )

    def clean(self):
        """Empêche deux étudiants différents d'utiliser le même numéro de téléphone"""
        if self.telephone_inscription:
            conflit = Inscription.objects.filter(
                telephone_inscription=self.telephone_inscription
            ).exclude(etudiant=self.etudiant)

            if self.pk:
                conflit = conflit.exclude(pk=self.pk)

            if conflit.exists():
                autre_inscription = conflit.first()
                raise ValidationError({
                    'telephone_inscription': (
                        f"Ce numéro de téléphone est déjà utilisé par un autre étudiant "
                        f"({autre_inscription.etudiant}). Chaque étudiant doit avoir un numéro unique."
                    )
                })

    def __str__(self):
        return f"{self.etudiant} - {self.filiere} ({self.annee_academique}) - {self.statut}"

    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ('etudiant', 'annee_academique')