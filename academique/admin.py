from django.contrib import admin
from .models import Filiere, Niveau, AnneeAcademique, Semestre


@admin.register(Filiere)
class FiliereAdmin(admin.ModelAdmin):
    list_display = ('nom_filiere', 'description')
    search_fields = ('nom_filiere',)


@admin.register(Niveau)
class NiveauAdmin(admin.ModelAdmin):
    list_display = ('libelle',)


@admin.register(AnneeAcademique)
class AnneeAcademiqueAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'date_debut', 'date_fin')


@admin.register(Semestre)
class SemestreAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'annee_academique', 'date_debut', 'date_fin')
    list_filter = ('annee_academique',)