from django.contrib import admin
from .models import Cours, Note


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('intitule', 'filiere', 'niveau', 'semestre', 'enseignant', 'credits')
    list_filter = ('filiere', 'niveau', 'semestre')
    search_fields = ('intitule',)


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'cours', 'valeur', 'type_evaluation', 'date_evaluation')
    list_filter = ('cours', 'type_evaluation')
    search_fields = ('etudiant__matricule',)