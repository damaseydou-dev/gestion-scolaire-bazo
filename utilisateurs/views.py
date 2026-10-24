import json
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from inscriptions.models import Inscription
from paiements.models import Paiement, FraisScolarite
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def connexion_view(request):
    """Page de connexion pour tous les utilisateurs (étudiant, enseignant, admin, caissier)"""
    if request.user.is_authenticated:
        return redirect('redirection_dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('redirection_dashboard')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    return render(request, 'utilisateurs/login.html')


def deconnexion_view(request):
    """Déconnexion de l'utilisateur"""
    logout(request)
    return redirect('login')


@login_required
def redirection_dashboard(request):
    """
    Redirige l'utilisateur vers le bon tableau de bord
    selon son rôle (étudiant, enseignant, admin, caissier)
    """
    role = request.user.role

    if role == 'etudiant':
        return redirect('dashboard_etudiant')
    elif role == 'enseignant':
        return redirect('dashboard_enseignant')
    elif role == 'admin':
        return redirect('dashboard_admin')
    elif role == 'caissier':
        return redirect('dashboard_caissier')
    else:
        messages.error(request, "Rôle utilisateur non reconnu.")
        return redirect('login')


@login_required
def dashboard_etudiant_view(request):
    """Tableau de bord de l'étudiant"""
    if request.user.role != 'etudiant':
        return redirect('redirection_dashboard')

    etudiant = request.user.profil_etudiant
    return render(request, 'utilisateurs/dashboard_etudiant.html', {
        'etudiant': etudiant
    })


@login_required
def dashboard_enseignant_view(request):
    """Tableau de bord de l'enseignant"""
    if request.user.role != 'enseignant':
        return redirect('redirection_dashboard')

    enseignant = request.user.profil_enseignant
    return render(request, 'utilisateurs/dashboard_enseignant.html', {
        'enseignant': enseignant
    })


@login_required
def dashboard_admin_view(request):
    """Tableau de bord de l'administrateur avec statistiques"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    # 1. Répartition des étudiants par filière (inscriptions validées)
    par_filiere = Inscription.objects.filter(statut='VALIDEE').values(
        'filiere__nom_filiere'
    ).annotate(total=Count('etudiant', distinct=True)).order_by('-total')

    labels_filiere = [item['filiere__nom_filiere'] for item in par_filiere]
    data_filiere = [item['total'] for item in par_filiere]

    # 2. Évolution des inscriptions par mois
    par_mois = Inscription.objects.annotate(
        mois=TruncMonth('date_inscription')
    ).values('mois').annotate(total=Count('id')).order_by('mois')

    labels_mois = [item['mois'].strftime('%b %Y') for item in par_mois]
    data_mois = [item['total'] for item in par_mois]

    # 3. Taux de paiement (total dû vs total payé)
    total_du = 0
    for inscription in Inscription.objects.filter(statut='VALIDEE'):
        frais = FraisScolarite.objects.filter(
            filiere=inscription.filiere,
            niveau=inscription.niveau,
            annee_academique=inscription.annee_academique
        ).first()
        if frais:
            total_du += frais.montant_total

    total_paye = Paiement.objects.aggregate(total=Sum('montant'))['total'] or 0
    total_restant = max(total_du - total_paye, 0)

    # 4. Répartition par statut d'inscription
    par_statut = Inscription.objects.values('statut').annotate(total=Count('id'))
    labels_statut_map = dict(Inscription.STATUT_CHOICES)
    labels_statut = [labels_statut_map.get(item['statut'], item['statut']) for item in par_statut]
    data_statut = [item['total'] for item in par_statut]

    context = {
        'labels_filiere': json.dumps(labels_filiere),
        'data_filiere': json.dumps(data_filiere),
        'labels_mois': json.dumps(labels_mois),
        'data_mois': json.dumps(data_mois),
        'total_paye': float(total_paye),
        'total_restant': float(total_restant),
        'labels_statut': json.dumps(labels_statut),
        'data_statut': json.dumps(data_statut),
    }

    return render(request, 'utilisateurs/dashboard_admin.html', context)