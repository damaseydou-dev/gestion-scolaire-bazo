from django.db import models
from academique.models import Filiere, Niveau, Semestre
from utilisateurs.models import Enseignant, Etudiant


class Cours(models.Model):
    intitule = models.CharField(max_length=150)
    credits = models.PositiveIntegerField(default=3)
    filiere = models.ForeignKey(
        Filiere,
        on_delete=models.CASCADE,
        related_name='cours'
    )
    niveau = models.ForeignKey(
        Niveau,
        on_delete=models.CASCADE,
        related_name='cours'
    )
    semestre = models.ForeignKey(
        Semestre,
        on_delete=models.CASCADE,
        related_name='cours'
    )
    enseignant = models.ForeignKey(
        Enseignant,
        on_delete=models.SET_NULL,
        related_name='cours',
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.intitule} ({self.niveau})"

    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"


class Note(models.Model):
    TYPE_EVALUATION_CHOICES = (
        ('DS', 'Devoir Surveillé'),
        ('EXAMEN', 'Examen'),
        ('TP', 'Travaux Pratiques'),
        ('AUTRE', 'Autre'),
    )

    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    cours = models.ForeignKey(
        Cours,
        on_delete=models.CASCADE,
        related_name='notes'
    )
    valeur = models.DecimalField(max_digits=5, decimal_places=2)
    type_evaluation = models.CharField(
        max_length=10,
        choices=TYPE_EVALUATION_CHOICES,
        default='EXAMEN'
    )
    date_evaluation = models.DateField()

    def __str__(self):
        return f"{self.etudiant} - {self.cours} : {self.valeur}/20"

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"


class Presence(models.Model):
    etudiant = models.ForeignKey(
        Etudiant,
        on_delete=models.CASCADE,
        related_name='presences'
    )
    cours = models.ForeignKey(
        Cours,
        on_delete=models.CASCADE,
        related_name='presences'
    )
    date_seance = models.DateField()
    present = models.BooleanField(default=True)

    def __str__(self):
        statut = "Présent" if self.present else "Absent"
        return f"{self.etudiant} - {self.cours} - {self.date_seance} - {statut}"

    class Meta:
        verbose_name = "Présence"
        verbose_name_plural = "Présences"
        unique_together = ('etudiant', 'cours', 'date_seance')