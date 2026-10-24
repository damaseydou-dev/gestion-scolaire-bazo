from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cours, Note
from inscriptions.models import Inscription
from academique.models import AnneeAcademique
from utilisateurs.models import Etudiant
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db.models import Count
from utilisateurs.models import Utilisateur
from .models import Presence
from django.core.mail import send_mail
from django.db.models import Sum
from paiements.models import FraisScolarite


def verifier_alerte_absences(etudiant):
    """Envoie une alerte si l'étudiant atteint exactement 3 absences au total"""
    total_absences = Presence.objects.filter(etudiant=etudiant, present=False).count()

    if total_absences == 3:
        destinataires = list(
            Utilisateur.objects.filter(role='admin').exclude(email='').values_list('email', flat=True)
        )

        cours_recent = Presence.objects.filter(
            etudiant=etudiant, present=False
        ).order_by('-date_seance').first()
        if cours_recent and cours_recent.cours.enseignant.utilisateur.email:
            destinataires.append(cours_recent.cours.enseignant.utilisateur.email)

        if destinataires:
            send_mail(
                subject="Alerte absentéisme - Université BAZO",
                message=(
                    f"Bonjour,\n\n"
                    f"L'étudiant {etudiant.utilisateur.first_name} {etudiant.utilisateur.last_name} "
                    f"(matricule {etudiant.matricule}) a atteint 3 absences, "
                    f"dont la plus récente lors du cours de {cours_recent.cours.intitule} "
                    f"le {cours_recent.date_seance}.\n"
                    f"Merci de vérifier sa situation.\n\n"
                    f"Cordialement,\nUniversité BAZO"
                ),
                from_email=None,
                recipient_list=destinataires,
                fail_silently=True,
            )


@login_required
def saisir_presences_view(request, cours_id):
    """Permet à l'enseignant de saisir les présences des étudiants"""
    if request.user.role != 'enseignant':
        return redirect('redirection_dashboard')

    cours = get_object_or_404(Cours, id=cours_id)

    if cours.enseignant != request.user.profil_enseignant:
        messages.error(request, "Vous n'êtes pas autorisé à saisir les présences de ce cours.")
        return redirect('mes_cours')

    inscriptions = Inscription.objects.filter(
        filiere=cours.filiere,
        niveau=cours.niveau,
        annee_academique=cours.semestre.annee_academique,
        statut='VALIDEE'
    ).select_related('etudiant', 'etudiant__utilisateur')

    if request.method == 'POST':
        date_seance = request.POST.get('date_seance')

        for inscription in inscriptions:
            etudiant = inscription.etudiant
            present = request.POST.get(f'present_{etudiant.id}') == 'on'

            presence, created = Presence.objects.update_or_create(
                etudiant=etudiant,
                cours=cours,
                date_seance=date_seance,
                defaults={'present': present}
            )

            if not present:
                verifier_alerte_absences(etudiant)

        messages.success(request, "Les présences ont été enregistrées avec succès.")
        return redirect('mes_cours')

    return render(request, 'cours/saisir_presences.html', {
        'cours': cours,
        'inscriptions': inscriptions
    })


@login_required
def mes_notes_view(request):
    """Affiche toutes les notes de l'étudiant connecté, avec recherche par cours"""
    if request.user.role != 'etudiant':
        return redirect('redirection_dashboard')

    etudiant = request.user.profil_etudiant
    recherche = request.GET.get('q', '').strip()

    notes = Note.objects.filter(etudiant=etudiant).select_related('cours').order_by('-date_evaluation')

    if recherche:
        notes = notes.filter(cours__intitule__icontains=recherche)

    return render(request, 'cours/mes_notes.html', {
        'notes': notes,
        'recherche': recherche
    })


@login_required
def mes_cours_view(request):
    """Affiche la liste des cours de l'enseignant connecté, avec recherche"""
    if request.user.role != 'enseignant':
        return redirect('redirection_dashboard')

    enseignant = request.user.profil_enseignant
    recherche = request.GET.get('q', '').strip()

    cours = Cours.objects.filter(enseignant=enseignant).select_related('filiere', 'niveau', 'semestre')

    if recherche:
        cours = cours.filter(intitule__icontains=recherche)

    return render(request, 'cours/mes_cours.html', {
        'liste_cours': cours,
        'recherche': recherche
    })


@login_required
def saisir_notes_view(request, cours_id):
    """
    Permet à l'enseignant de saisir les notes des étudiants
    inscrits dans la filière/niveau du cours sélectionné
    """
    if request.user.role != 'enseignant':
        return redirect('redirection_dashboard')

    cours = get_object_or_404(Cours, id=cours_id)

    if cours.enseignant != request.user.profil_enseignant:
        messages.error(request, "Vous n'êtes pas autorisé à saisir les notes de ce cours.")
        return redirect('mes_cours')

    inscriptions = Inscription.objects.filter(
        filiere=cours.filiere,
        niveau=cours.niveau,
        annee_academique=cours.semestre.annee_academique,
        statut='VALIDEE'
    ).select_related('etudiant', 'etudiant__utilisateur')

    if request.method == 'POST':
        for inscription in inscriptions:
            etudiant = inscription.etudiant
            valeur = request.POST.get(f'note_{etudiant.id}')
            type_evaluation = request.POST.get(f'type_{etudiant.id}')
            date_evaluation = request.POST.get('date_evaluation')

            if valeur:
                Note.objects.update_or_create(
                    etudiant=etudiant,
                    cours=cours,
                    type_evaluation=type_evaluation,
                    date_evaluation=date_evaluation,
                    defaults={'valeur': valeur}
                )

        messages.success(request, "Les notes ont été enregistrées avec succès.")
        return redirect('mes_cours')

    return render(request, 'cours/saisir_notes.html', {
        'cours': cours,
        'inscriptions': inscriptions
    })


@login_required
def liste_etudiants_releve_view(request):
    """Liste des étudiants pour lesquels l'administrateur peut générer un relevé de notes"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    recherche = request.GET.get('q', '').strip()

    etudiants = Etudiant.objects.select_related('utilisateur').all()

    if recherche:
        etudiants = etudiants.filter(matricule__icontains=recherche) | \
                    etudiants.filter(utilisateur__first_name__icontains=recherche) | \
                    etudiants.filter(utilisateur__last_name__icontains=recherche) | \
                    etudiants.filter(inscriptions__telephone_inscription__icontains=recherche)
        etudiants = etudiants.distinct()

    return render(request, 'cours/liste_etudiants_releve.html', {
        'etudiants': etudiants,
        'recherche': recherche
    })


def calculer_mention(moyenne):
    if moyenne is None:
        return "-"
    if moyenne >= 16:
        return "Très Bien"
    elif moyenne >= 14:
        return "Bien"
    elif moyenne >= 12:
        return "Assez Bien"
    elif moyenne >= 10:
        return "Passable"
    else:
        return "Insuffisant"


@login_required
def releve_notes_view(request, etudiant_id):
    """Génère le relevé de notes d'un étudiant pour une année académique donnée"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    etudiant = get_object_or_404(Etudiant, id=etudiant_id)

    annee_ids = Note.objects.filter(etudiant=etudiant).values_list(
        'cours__semestre__annee_academique_id', flat=True
    ).distinct()
    annees_disponibles = AnneeAcademique.objects.filter(id__in=annee_ids)

    annee_id = request.GET.get('annee')
    annee_selectionnee = None
    lignes_releve = []
    moyenne_generale = None
    total_credits = 0

    if annee_id:
        annee_selectionnee = get_object_or_404(AnneeAcademique, id=annee_id)

        notes = Note.objects.filter(
            etudiant=etudiant,
            cours__semestre__annee_academique=annee_selectionnee
        ).select_related('cours')

        cours_notes = {}
        for note in notes:
            cours_notes.setdefault(note.cours, []).append(note.valeur)

        somme_ponderee = 0
        for cours, valeurs in cours_notes.items():
            moyenne_cours = sum(valeurs) / len(valeurs)
            lignes_releve.append({
                'cours': cours,
                'moyenne': round(moyenne_cours, 2),
                'credits': cours.credits,
            })
            somme_ponderee += moyenne_cours * cours.credits
            total_credits += cours.credits

        if total_credits > 0:
            moyenne_generale = round(somme_ponderee / total_credits, 2)

    inscription = Inscription.objects.filter(
        etudiant=etudiant,
        annee_academique=annee_selectionnee
    ).first() if annee_selectionnee else None

    return render(request, 'cours/releve_notes.html', {
        'etudiant': etudiant,
        'annees_disponibles': annees_disponibles,
        'annee_selectionnee': annee_selectionnee,
        'lignes_releve': lignes_releve,
        'moyenne_generale': moyenne_generale,
        'mention': calculer_mention(moyenne_generale),
        'total_credits': total_credits,
        'inscription': inscription,
    })


@login_required
def releve_notes_pdf_view(request, etudiant_id):
    """Génère le relevé de notes en PDF téléchargeable"""
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')

    etudiant = get_object_or_404(Etudiant, id=etudiant_id)
    annee_id = request.GET.get('annee')

    annee_selectionnee = None
    lignes_releve = []
    moyenne_generale = None
    total_credits = 0

    if annee_id:
        annee_selectionnee = get_object_or_404(AnneeAcademique, id=annee_id)

        notes = Note.objects.filter(
            etudiant=etudiant,
            cours__semestre__annee_academique=annee_selectionnee
        ).select_related('cours')

        cours_notes = {}
        for note in notes:
            cours_notes.setdefault(note.cours, []).append(note.valeur)

        somme_ponderee = 0
        for cours, valeurs in cours_notes.items():
            moyenne_cours = sum(valeurs) / len(valeurs)
            lignes_releve.append({
                'cours': cours,
                'moyenne': round(moyenne_cours, 2),
                'credits': cours.credits,
            })
            somme_ponderee += moyenne_cours * cours.credits
            total_credits += cours.credits

        if total_credits > 0:
            moyenne_generale = round(somme_ponderee / total_credits, 2)

    inscription = Inscription.objects.filter(
        etudiant=etudiant,
        annee_academique=annee_selectionnee
    ).first() if annee_selectionnee else None

    context = {
        'etudiant': etudiant,
        'annee_selectionnee': annee_selectionnee,
        'lignes_releve': lignes_releve,
        'moyenne_generale': moyenne_generale,
        'mention': calculer_mention(moyenne_generale),
        'total_credits': total_credits,
        'inscription': inscription,
    }

    template = get_template('cours/releve_notes_pdf.html')
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="releve_{etudiant.matricule}.pdf"'

    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Erreur lors de la génération du PDF', status=500)

    return response


def construire_parcours(etudiant):
    """Une entrée par inscription : année, résultats et situation financière"""
    inscriptions = Inscription.objects.filter(etudiant=etudiant).select_related(
        'filiere', 'niveau', 'annee_academique'
    ).order_by('annee_academique__libelle')

    parcours = []
    for insc in inscriptions:
        notes = Note.objects.filter(
            etudiant=etudiant,
            cours__semestre__annee_academique=insc.annee_academique
        ).select_related('cours')

        cours_notes = {}
        for note in notes:
            cours_notes.setdefault(note.cours, []).append(note.valeur)

        somme, credits = 0, 0
        for cours, valeurs in cours_notes.items():
            somme += (sum(valeurs) / len(valeurs)) * cours.credits
            credits += cours.credits
        moyenne = round(somme / credits, 2) if credits > 0 else None

        frais = FraisScolarite.objects.filter(
            filiere=insc.filiere, niveau=insc.niveau,
            annee_academique=insc.annee_academique
        ).first()
        total = frais.montant_total if frais else 0
        a_payer = max(total - insc.remise, 0)
        paye = insc.paiements.aggregate(t=Sum('montant'))['t'] or 0

        parcours.append({
            'inscription': insc,
            'moyenne': moyenne,
            'mention': calculer_mention(moyenne),
            'credits': credits,
            'total': total,
            'remise': insc.remise,
            'paye': paye,
            'reste': max(a_payer - paye, 0),
        })
    return parcours


@login_required
def mon_parcours_view(request):
    if request.user.role != 'etudiant':
        return redirect('redirection_dashboard')
    etudiant = request.user.profil_etudiant
    return render(request, 'cours/parcours.html', {
        'etudiant': etudiant,
        'parcours': construire_parcours(etudiant),
        'est_admin': False,
    })


@login_required
def parcours_etudiant_view(request, etudiant_id):
    if request.user.role != 'admin':
        return redirect('redirection_dashboard')
    etudiant = get_object_or_404(Etudiant, id=etudiant_id)
    return render(request, 'cours/parcours.html', {
        'etudiant': etudiant,
        'parcours': construire_parcours(etudiant),
        'est_admin': True,
    })