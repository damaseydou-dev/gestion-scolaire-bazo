from django.urls import path
from . import views

urlpatterns = [
    path('mes-notes/', views.mes_notes_view, name='mes_notes'),
    path('mes-cours/', views.mes_cours_view, name='mes_cours'),
    path('saisir-notes/<int:cours_id>/', views.saisir_notes_view, name='saisir_notes'),
    path('releve/', views.liste_etudiants_releve_view, name='liste_etudiants_releve'),
    path('releve/<int:etudiant_id>/', views.releve_notes_view, name='releve_notes'),
    path('releve/<int:etudiant_id>/pdf/', views.releve_notes_pdf_view, name='releve_notes_pdf'),
    path('saisir-presences/<int:cours_id>/', views.saisir_presences_view, name='saisir_presences'),
    path('mon-parcours/', views.mon_parcours_view, name='mon_parcours'),
    path('parcours/<int:etudiant_id>/', views.parcours_etudiant_view, name='parcours_etudiant'),
]