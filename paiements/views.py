from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from datetime import date
from .models import FraisScolarite, Paiement
from inscriptions.models import Inscription
from academique.models import Filiere, Niveau, AnneeAcademique


def calculer_solde(inscription):
    """Calcule le solde restant à payer pour une inscription donnée, en tenant compte de la remise"""
    try:
        frais = FraisScolarite.objects.get(
            filiere=inscription.filiere,
            niveau=inscription.niveau,
            annee_academique=inscription.annee_academique
        )
        montant_total = frais.montant_total
    except FraisScolarite.DoesNotExist:
        frais = None
        montant_total = 0

    remise = inscription.remise or 0
    montant_du = montant_total - remise
    montant_paye = inscription.paiements.aggregate(total=Sum('montant'))['total'] or 0
    solde = montant_du - montant_paye

    return {
        'frais': frais,
        'montant_total': montant_total,
        'remise': remise,
        'montant_du': montant_du,
        'montant_paye': montant_paye,
        'solde': solde,
    }


def calculer_statut_paiement(inscription, infos_solde):
    """Détermine si l'étudiant est 'À jour' ou 'En retard' selon les échéances passées"""
    frais = infos_solde['frais']
    if not frais:
        return "Non défini"

    aujourd_hui = date.today()
    montant_attendu_a_ce_jour = frais.echeances.filter(
        date_echeance__lte=aujourd_hui
    ).aggregate(total=Sum('montant_attendu'))['total'] or 0

    montant_attendu_net = montant_attendu_a_ce_jour - infos_solde['remise']
    if montant_attendu_net < 0:
        montant_attendu_net = 0

    if infos_solde['montant_paye'] >= montant_attendu_net:
        return "À jour"
    else:
        return "En retard"


@login_required
def dashboard_caissier_view(request):
    """Liste des étudiants inscrits (validés) avec leur solde, avec recherche par téléphone/nom/matricule"""
    if request.user.role != 'caissier':
        return redirect('redirection_dashboard')

    recherche = request.GET.get('q', '').strip()

    inscriptions = Inscription.objects.filter(statut='VALIDEE').select_related(
        'etudiant', 'etudiant__utilisateur', 'filiere', 'niveau', 'annee_academique'
    )

    if recherche:
        inscriptions = inscriptions.filter(
            telephone_inscription__icontains=recherche
        ) | inscriptions.filter(
            etudiant__matricule__icontains=recherche
        ) | inscriptions.filter(
            etudiant__utilisateur__first_name__icontains=recherche
        ) | inscriptions.filter(
            etudiant__utilisateur__last_name__icontains=recherche
        )
        inscriptions = inscriptions.distinct()

    donnees = []
    for inscription in inscriptions:
        infos = calculer_solde(inscription)
        donnees.append({
            'inscription': inscription,
            'montant_total': infos['montant_total'],
            'remise': infos['remise'],
            'montant_paye': infos['montant_paye'],
            'solde': infos['solde'],
        })

    return render(request, 'paiements/dashboard_caissier.html', {
        'donnees': donnees,
        'recherche': recherche
    })


@login_required
def enregistrer_paiement_view(request, inscription_id):
    """Formulaire pour enregistrer un nouveau versement pour un étudiant"""
    if request.user.role != 'caissier':
        return redirect('redirection_dashboard')

    inscription = get_object_or_404(Inscription, id=inscription_id)
    caissier = request.user.profil_caissier

    infos = calculer_solde(inscription)
    nb_tranches_existantes = inscription.paiements.count()

    if request.method == 'POST':
        if nb_tranches_existantes >= 3:
            messages.error(request, "Le nombre maximum de tranches (3) a déjà été atteint pour cet étudiant.")
        else:
            montant = request.POST.get('montant')
            mode_paiement = request.POST.get('mode_paiement')
            date_paiement = request.POST.get('date_paiement')

            if float(montant) > float(infos['solde']):
                messages.error(request, f"Le montant saisi dépasse le solde restant ({infos['solde']} FCFA).")
            else:
                paiement = Paiement.objects.create(
                    inscription=inscription,
                    numero_tranche=nb_tranches_existantes + 1,
                    montant=montant,
                    mode_paiement=mode_paiement,
                    date_paiement=date_paiement,
                    enregistre_par=caissier
                )
                messages.success(request, "Paiement enregistré avec succès.")
                return redirect('recu_paiement', paiement_id=paiement.id)

    return render(request, 'paiements/enregistrer_paiement.html', {
        'inscription': inscription,
        'montant_total': infos['montant_total'],
        'remise': infos['remise'],
        'montant_paye': infos['montant_paye'],
        'solde': infos['solde'],
        'nb_tranches_existantes': nb_tranches_existantes,
    })


@login_required
def recu_paiement_view(request, paiement_id):
    """Affiche le reçu imprimable d'un paiement"""
    paiement = get_object_or_404(Paiement, id=paiement_id)
    inscription = paiement.inscription

    if request.user.role not in ['caissier', 'admin']:
        return redirect('redirection_dashboard')

    infos = calculer_solde(inscription)

    return render(request, 'paiements/recu_paiement.html', {
        'paiement': paiement,
        'inscription': inscription,
        'montant_total': infos['montant_total'],
        'remise': infos['remise'],
        'montant_paye': infos['montant_paye'],
        'solde': infos['solde'],
    })


@login_required
def historique_paiements_view(request, inscription_id):
    """Liste tous les paiements effectués pour une inscription, avec lien vers chaque reçu"""
    if request.user.role != 'caissier':
        return redirect('redirection_dashboard')

    inscription = get_object_or_404(Inscription, id=inscription_id)
    paiements = inscription.paiements.all().order_by('numero_tranche')

    return render(request, 'paiements/historique_paiements.html', {
        'inscription': inscription,
        'paiements': paiements
    })


@login_required
def ma_scolarite_view(request):
    """Page étudiant : montant, remise, échéances, statut de paiement"""
    if request.user.role != 'etudiant':
        return redirect('redirection_dashboard')

    etudiant = request.user.profil_etudiant
    inscription = Inscription.objects.filter(
        etudiant=etudiant, statut='VALIDEE'
    ).order_by('-date_inscription').first()

    if not inscription:
        return render(request, 'paiements/ma_scolarite.html', {'inscription': None})

    infos = calculer_solde(inscription)
    statut = calculer_statut_paiement(inscription, infos)
    echeances = infos['frais'].echeances.all() if infos['frais'] else []
    paiements = inscription.paiements.all().order_by('numero_tranche')

    return render(request, 'paiements/ma_scolarite.html', {
        'inscription': inscription,
        'montant_total': infos['montant_total'],
        'remise': infos['remise'],
        'montant_du': infos['montant_du'],
        'montant_paye': infos['montant_paye'],
        'solde': infos['solde'],
        'statut': statut,
        'echeances': echeances,
        'paiements': paiements,
    })


@login_required
def effectif_view(request):
    """Affiche l'effectif total des étudiants inscrits (validés), pour l'admin"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    inscriptions = Inscription.objects.filter(statut='VALIDEE').select_related('filiere', 'niveau', 'annee_academique')
    total = inscriptions.count()

    repartition = {}
    for inscription in inscriptions:
        cle = f"{inscription.filiere} - {inscription.niveau}"
        repartition[cle] = repartition.get(cle, 0) + 1

    return render(request, 'paiements/effectif.html', {
        'total': total,
        'repartition': repartition
    })


@login_required
def liste_classes_view(request):
    """Liste toutes les classes (filière + niveau + année) avec leur effectif, pour l'admin"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    inscriptions = Inscription.objects.filter(statut='VALIDEE').select_related(
        'filiere', 'niveau', 'annee_academique'
    )

    classes = {}
    for inscription in inscriptions:
        cle = (inscription.filiere, inscription.niveau, inscription.annee_academique)
        classes[cle] = classes.get(cle, 0) + 1

    liste_classes = [
        {
            'filiere': filiere,
            'niveau': niveau,
            'annee': annee,
            'effectif': effectif
        }
        for (filiere, niveau, annee), effectif in classes.items()
    ]

    return render(request, 'paiements/liste_classes.html', {
        'liste_classes': liste_classes
    })


@login_required
def liste_etudiants_classe_view(request, filiere_id, niveau_id, annee_id):
    """Affiche la liste imprimable des étudiants d'une classe précise, pour l'appel"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    filiere = get_object_or_404(Filiere, id=filiere_id)
    niveau = get_object_or_404(Niveau, id=niveau_id)
    annee = get_object_or_404(AnneeAcademique, id=annee_id)

    inscriptions = Inscription.objects.filter(
        filiere=filiere,
        niveau=niveau,
        annee_academique=annee,
        statut='VALIDEE'
    ).select_related('etudiant', 'etudiant__utilisateur').order_by(
        'etudiant__utilisateur__last_name', 'etudiant__utilisateur__first_name'
    )

    return render(request, 'paiements/liste_etudiants_classe.html', {
        'filiere': filiere,
        'niveau': niveau,
        'annee': annee,
        'inscriptions': inscriptions
    })


@login_required
def carte_etudiant_view(request, etudiant_id):
    """Génère la carte d'étudiant imprimable, pour l'admin"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    from utilisateurs.models import Etudiant
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)

    inscription = Inscription.objects.filter(
        etudiant=etudiant, statut='VALIDEE'
    ).select_related('filiere', 'niveau', 'annee_academique').order_by('-date_inscription').first()

    return render(request, 'paiements/carte_etudiant.html', {
        'etudiant': etudiant,
        'inscription': inscription
    })