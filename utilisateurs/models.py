from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator

validateur_telephone = RegexValidator(
    regex=r'^\d{8}$',
    message="Le numéro de téléphone doit contenir exactement 8 chiffres (ex: 70123456)."
)


class Utilisateur(AbstractUser):
    """
    Étend le modèle utilisateur par défaut de Django.
    Django gère déjà : username, email, password, first_name, last_name
    """
    ROLE_CHOICES = (
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('admin', 'Administrateur'),
        ('caissier', 'Caissier'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    telephone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.role})"


class Etudiant(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='profil_etudiant'
    )
    matricule = models.CharField(max_length=20, unique=True)
    date_naissance = models.DateField(blank=True, null=True)
    lieu_naissance = models.CharField(max_length=100, blank=True, null=True)
    telephone_parent = models.CharField(
        max_length=8,
        blank=True,
        null=True,
        validators=[validateur_telephone],
        verbose_name="Téléphone du parent/tuteur (contact d'urgence)"
    )
    photo = models.ImageField(
        upload_to='photos_etudiants/',
        blank=True,
        null=True,
        verbose_name="Photo d'identité"
    )

    def __str__(self):
        return f"Étudiant: {self.matricule} - {self.utilisateur}"


class Enseignant(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='profil_enseignant'
    )
    matricule = models.CharField(max_length=20, unique=True)
    specialite = models.CharField(max_length=100, blank=True, null=True)
    grade = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"Enseignant: {self.matricule} - {self.utilisateur}"


class Administrateur(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='profil_administrateur'
    )
    fonction = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Admin: {self.fonction} - {self.utilisateur}"


class Caissier(models.Model):
    utilisateur = models.OneToOneField(
        Utilisateur,
        on_delete=models.CASCADE,
        related_name='profil_caissier'
    )
    matricule = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Caissier: {self.matricule} - {self.utilisateur}"