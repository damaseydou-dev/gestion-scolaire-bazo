from django.contrib import admin
from .models import Inscription


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'telephone_inscription', 'filiere', 'niveau', 'annee_academique', 'statut', 'date_inscription')
    list_filter = ('statut', 'filiere', 'annee_academique')
    search_fields = ('etudiant__matricule', 'telephone_inscription', 'etudiant__utilisateur__first_name', 'etudiant__utilisateur__last_name')
    list_editable = ('statut',)