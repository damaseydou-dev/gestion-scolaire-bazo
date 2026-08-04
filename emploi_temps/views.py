from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import EmploiDuTemps, Salle
from inscriptions.models import Inscription

ORDRE_JOURS = ['LUNDI', 'MARDI', 'MERCREDI', 'JEUDI', 'VENDREDI', 'SAMEDI']


@login_required
def emploi_temps_etudiant_view(request):
    """Affiche l'emploi du temps de l'étudiant selon sa filière/niveau/année inscrite"""
    if request.user.role != 'etudiant':
        return redirect('redirection_dashboard')

    etudiant = request.user.profil_etudiant

    inscription = Inscription.objects.filter(
        etudiant=etudiant,
        statut='VALIDEE'
    ).select_related('filiere', 'niveau', 'annee_academique').order_by('-date_inscription').first()

    creneaux = []
    if inscription:
        creneaux = EmploiDuTemps.objects.filter(
            cours__filiere=inscription.filiere,
            cours__niveau=inscription.niveau,
            cours__semestre__annee_academique=inscription.annee_academique
        ).select_related('cours', 'enseignant', 'salle')

        creneaux = sorted(creneaux, key=lambda c: (ORDRE_JOURS.index(c.jour_semaine), c.heure_debut))

    return render(request, 'emploi_temps/emploi_temps_etudiant.html', {
        'creneaux': creneaux,
        'inscription': inscription
    })


@login_required
def emploi_temps_enseignant_view(request):
    """Affiche l'emploi du temps de l'enseignant connecté"""
    if request.user.role != 'enseignant':
        return redirect('redirection_dashboard')

    enseignant = request.user.profil_enseignant

    creneaux = EmploiDuTemps.objects.filter(
        enseignant=enseignant
    ).select_related('cours', 'salle')

    creneaux = sorted(creneaux, key=lambda c: (ORDRE_JOURS.index(c.jour_semaine), c.heure_debut))

    return render(request, 'emploi_temps/emploi_temps_enseignant.html', {
        'creneaux': creneaux
    })


@login_required
def disponibilite_salles_view(request):
    """Affiche pour chaque salle son occupation par jour, pour aider à planifier sans conflit"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    salles = Salle.objects.all()
    tableau = []

    for salle in salles:
        creneaux = EmploiDuTemps.objects.filter(salle=salle).select_related('cours', 'enseignant')
        creneaux = sorted(creneaux, key=lambda c: (ORDRE_JOURS.index(c.jour_semaine), c.heure_debut))
        tableau.append({
            'salle': salle,
            'creneaux': creneaux
        })

    return render(request, 'emploi_temps/disponibilite_salles.html', {
        'tableau': tableau
    })