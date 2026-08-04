from django.db import models
from django.core.exceptions import ValidationError
from cours.models import Cours
from utilisateurs.models import Enseignant


class Salle(models.Model):
    nom = models.CharField(max_length=50)
    capacite = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.nom} ({self.capacite} places)"

    class Meta:
        verbose_name = "Salle"
        verbose_name_plural = "Salles"


class EmploiDuTemps(models.Model):
    JOUR_CHOICES = (
        ('LUNDI', 'Lundi'),
        ('MARDI', 'Mardi'),
        ('MERCREDI', 'Mercredi'),
        ('JEUDI', 'Jeudi'),
        ('VENDREDI', 'Vendredi'),
        ('SAMEDI', 'Samedi'),
    )

    cours = models.ForeignKey(
        Cours,
        on_delete=models.CASCADE,
        related_name='creneaux'
    )
    enseignant = models.ForeignKey(
        Enseignant,
        on_delete=models.CASCADE,
        related_name='creneaux'
    )
    salle = models.ForeignKey(
        Salle,
        on_delete=models.CASCADE,
        related_name='creneaux'
    )
    jour_semaine = models.CharField(max_length=10, choices=JOUR_CHOICES)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    def clean(self):
        if self.heure_debut and self.heure_fin and self.heure_debut >= self.heure_fin:
            raise ValidationError({
                'heure_fin': "L'heure de fin doit être après l'heure de début."
            })

        if self.enseignant_id and self.jour_semaine and self.heure_debut and self.heure_fin:
            # --- Conflit enseignant : déjà occupé sur un autre cours au même moment ---
            conflits_enseignant = EmploiDuTemps.objects.filter(
                enseignant=self.enseignant,
                jour_semaine=self.jour_semaine,
                heure_debut__lt=self.heure_fin,
                heure_fin__gt=self.heure_debut,
            )
            if self.pk:
                conflits_enseignant = conflits_enseignant.exclude(pk=self.pk)

            if conflits_enseignant.exists():
                creneau_conflit = conflits_enseignant.first()
                raise ValidationError(
                    f"Conflit d'emploi du temps : {self.enseignant} a déjà un cours "
                    f"({creneau_conflit.cours}) le {self.get_jour_semaine_display()} "
                    f"de {creneau_conflit.heure_debut} à {creneau_conflit.heure_fin}."
                )

        if self.salle_id and self.jour_semaine and self.heure_debut and self.heure_fin:
            # --- Conflit de salle : déjà occupée par un autre cours au même moment ---
            conflits_salle = EmploiDuTemps.objects.filter(
                salle=self.salle,
                jour_semaine=self.jour_semaine,
                heure_debut__lt=self.heure_fin,
                heure_fin__gt=self.heure_debut,
            )
            if self.pk:
                conflits_salle = conflits_salle.exclude(pk=self.pk)

            if conflits_salle.exists():
                creneau_conflit = conflits_salle.first()
                raise ValidationError(
                    f"Salle déjà occupée : {self.salle} est déjà réservée pour "
                    f"{creneau_conflit.cours} le {self.get_jour_semaine_display()} "
                    f"de {creneau_conflit.heure_debut} à {creneau_conflit.heure_fin}. "
                    f"Choisissez une autre salle ou un autre créneau."
                )

        # --- Alerte capacité : la salle est-elle assez grande pour la classe ? ---
        if self.salle_id and self.cours_id:
            from inscriptions.models import Inscription
            effectif = Inscription.objects.filter(
                filiere=self.cours.filiere,
                niveau=self.cours.niveau,
                annee_academique=self.cours.semestre.annee_academique,
                statut='VALIDEE'
            ).count()

            if effectif > self.salle.capacite:
                raise ValidationError(
                    f"Capacité insuffisante : la salle {self.salle} ne peut accueillir que "
                    f"{self.salle.capacite} personnes, mais {effectif} étudiants sont inscrits "
                    f"dans {self.cours.filiere} - {self.cours.niveau}. Choisissez une salle plus grande."
                )

    def __str__(self):
        return f"{self.cours} - {self.jour_semaine} {self.heure_debut}-{self.heure_fin}"

    class Meta:
        verbose_name = "Emploi du temps"
        verbose_name_plural = "Emplois du temps"