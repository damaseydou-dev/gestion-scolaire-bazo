from django.db import models


class Filiere(models.Model):
    nom_filiere = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nom_filiere

    class Meta:
        verbose_name = "Filière"
        verbose_name_plural = "Filières"


class Niveau(models.Model):
    libelle = models.CharField(max_length=20)  # ex: L1, L2, L3, M1, M2

    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name = "Niveau"
        verbose_name_plural = "Niveaux"


class AnneeAcademique(models.Model):
    libelle = models.CharField(max_length=20)  # ex: 2026-2027
    date_debut = models.DateField()
    date_fin = models.DateField()

    def __str__(self):
        return self.libelle

    class Meta:
        verbose_name = "Année académique"
        verbose_name_plural = "Années académiques"


class Semestre(models.Model):
    annee_academique = models.ForeignKey(
        AnneeAcademique,
        on_delete=models.CASCADE,
        related_name='semestres'
    )
    libelle = models.CharField(max_length=20)  # ex: Semestre 1
    date_debut = models.DateField()
    date_fin = models.DateField()

    def __str__(self):
        return f"{self.libelle} - {self.annee_academique}"

    class Meta:
        verbose_name = "Semestre"
        verbose_name_plural = "Semestres"