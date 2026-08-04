from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.connexion_view, name='login'),
    path('logout/', views.deconnexion_view, name='logout'),
    path('dashboard/', views.redirection_dashboard, name='redirection_dashboard'),
    path('dashboard/etudiant/', views.dashboard_etudiant_view, name='dashboard_etudiant'),
    path('dashboard/enseignant/', views.dashboard_enseignant_view, name='dashboard_enseignant'),
    path('dashboard/admin/', views.dashboard_admin_view, name='dashboard_admin'),
]