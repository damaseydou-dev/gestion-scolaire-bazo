from django.contrib import admin
from .models import FraisScolarite, EcheancePaiement, Paiement


class EcheancePaiementInline(admin.TabularInline):
    model = EcheancePaiement
    extra = 3


@admin.register(FraisScolarite)
class FraisScolariteAdmin(admin.ModelAdmin):
    list_display = ('filiere', 'niveau', 'annee_academique', 'montant_total')
    list_filter = ('filiere', 'niveau', 'annee_academique')
    inlines = [EcheancePaiementInline]


@admin.register(Paiement)
class PaiementAdmin(admin.ModelAdmin):
    list_display = ('inscription', 'numero_tranche', 'montant', 'mode_paiement', 'date_paiement', 'enregistre_par')
    list_filter = ('mode_paiement', 'date_paiement')
    search_fields = ('inscription__etudiant__matricule',)