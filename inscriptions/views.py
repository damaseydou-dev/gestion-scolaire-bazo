from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Inscription
from academique.models import Filiere, Niveau, AnneeAcademique


@login_required
def demande_inscription_view(request):
    """Permet à un étudiant de soumettre une demande d'inscription"""
    if request.user.role != 'etudiant':
        return redirect('redirection_dashboard')

    etudiant = request.user.profil_etudiant

    filieres = Filiere.objects.all()
    niveaux = Niveau.objects.all()
    annees = AnneeAcademique.objects.all()

    if request.method == 'POST':
        filiere_id = request.POST.get('filiere')
        niveau_id = request.POST.get('niveau')
        annee_id = request.POST.get('annee_academique')
        telephone_inscription = request.POST.get('telephone_inscription')
        telephone_parent = request.POST.get('telephone_parent')

        # Vérifier si une inscription existe déjà pour cette année
        deja_inscrit = Inscription.objects.filter(
            etudiant=etudiant,
            annee_academique_id=annee_id
        ).exists()

        if deja_inscrit:
            messages.error(request, "Vous avez déjà une demande d'inscription pour cette année académique.")
        else:
            nouvelle_inscription = Inscription(
                etudiant=etudiant,
                filiere_id=filiere_id,
                niveau_id=niveau_id,
                annee_academique_id=annee_id,
                telephone_inscription=telephone_inscription,
                statut='EN_ATTENTE'
            )

            try:
                nouvelle_inscription.full_clean()
                nouvelle_inscription.save()

                # On enregistre aussi le téléphone du parent sur le profil étudiant
                if telephone_parent:
                    etudiant.telephone_parent = telephone_parent
                    etudiant.save()

                messages.success(request, "Votre demande d'inscription a été soumise avec succès. Elle est en attente de validation par l'administration.")
                return redirect('mes_inscriptions')

            except ValidationError as e:
                for erreurs in e.message_dict.values():
                    for erreur in erreurs:
                        messages.error(request, erreur)

    return render(request, 'inscriptions/demande_inscription.html', {
        'filieres': filieres,
        'niveaux': niveaux,
        'annees': annees,
        'telephone_parent_actuel': etudiant.telephone_parent
    })


@login_required
def mes_inscriptions_view(request):
    """Affiche l'historique des demandes d'inscription de l'étudiant"""
    if request.user.role != 'etudiant':
        return redirect('redirection_dashboard')

    etudiant = request.user.profil_etudiant
    inscriptions = Inscription.objects.filter(etudiant=etudiant).select_related(
        'filiere', 'niveau', 'annee_academique'
    ).order_by('-date_inscription')

    return render(request, 'inscriptions/mes_inscriptions.html', {
        'inscriptions': inscriptions
    })