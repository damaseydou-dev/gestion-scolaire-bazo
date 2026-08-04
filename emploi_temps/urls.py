from django.urls import path
from . import views

urlpatterns = [
    path('etudiant/', views.emploi_temps_etudiant_view, name='emploi_temps_etudiant'),
    path('enseignant/', views.emploi_temps_enseignant_view, name='emploi_temps_enseignant'),
    path('disponibilite-salles/', views.disponibilite_salles_view, name='disponibilite_salles'),
]