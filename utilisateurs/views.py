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
    """Tableau de bord de l'administrateur"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    return render(request, 'utilisateurs/dashboard_admin.html')