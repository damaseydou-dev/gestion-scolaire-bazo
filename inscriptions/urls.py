from django.urls import path
from . import views

urlpatterns = [
    path('demande/', views.demande_inscription_view, name='demande_inscription'),
    path('mes-inscriptions/', views.mes_inscriptions_view, name='mes_inscriptions'),
]