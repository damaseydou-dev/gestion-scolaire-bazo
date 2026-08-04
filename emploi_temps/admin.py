from django.contrib import admin
from .models import Salle, EmploiDuTemps


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'capacite')


@admin.register(EmploiDuTemps)
class EmploiDuTempsAdmin(admin.ModelAdmin):
    list_display = ('cours', 'enseignant', 'salle', 'jour_semaine', 'heure_debut', 'heure_fin')
    list_filter = ('jour_semaine', 'salle')