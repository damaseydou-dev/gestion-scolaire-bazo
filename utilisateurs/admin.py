from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur, Etudiant, Enseignant, Administrateur, Caissier


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'email', 'role')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('role', 'telephone')}),
    )


@admin.register(Etudiant)
class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'utilisateur', 'date_naissance', 'telephone_parent')
    search_fields = ('matricule', 'telephone_parent')


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'utilisateur', 'specialite', 'grade')
    search_fields = ('matricule',)


@admin.register(Administrateur)
class AdministrateurAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'fonction')


@admin.register(Caissier)
class CaissierAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'utilisateur')
    search_fields = ('matricule',)