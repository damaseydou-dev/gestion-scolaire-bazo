from django.urls import path
from . import views

urlpatterns = [
    path('caissier/', views.dashboard_caissier_view, name='dashboard_caissier'),
    path('enregistrer/<int:inscription_id>/', views.enregistrer_paiement_view, name='enregistrer_paiement'),
    path('recu/<int:paiement_id>/', views.recu_paiement_view, name='recu_paiement'),
    path('historique/<int:inscription_id>/', views.historique_paiements_view, name='historique_paiements'),
    path('effectif/', views.effectif_view, name='effectif'),
    path('ma-scolarite/', views.ma_scolarite_view, name='ma_scolarite'),
    path('classes/', views.liste_classes_view, name='liste_classes'),
    path('classes/<int:filiere_id>/<int:niveau_id>/<int:annee_id>/', views.liste_etudiants_classe_view, name='liste_etudiants_classe'),
    path('carte/<int:etudiant_id>/', views.carte_etudiant_view, name='carte_etudiant'),
]