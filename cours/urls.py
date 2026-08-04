from django.urls import path
from . import views

urlpatterns = [
    path('mes-notes/', views.mes_notes_view, name='mes_notes'),
    path('mes-cours/', views.mes_cours_view, name='mes_cours'),
    path('saisir-notes/<int:cours_id>/', views.saisir_notes_view, name='saisir_notes'),
    path('releve/', views.liste_etudiants_releve_view, name='liste_etudiants_releve'),
    path('releve/<int:etudiant_id>/', views.releve_notes_view, name='releve_notes'),
]