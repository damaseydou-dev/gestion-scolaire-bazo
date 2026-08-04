"""
Script de réinitialisation des données de test.
Usage : python seed_data.py (a la racine du projet, meme niveau que manage.py)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_scolaire.settings')
django.setup()

from datetime import date, time
from utilisateurs.models import Utilisateur, Etudiant, Enseignant
from academique.models import Filiere, Niveau, AnneeAcademique, Semestre
from cours.models import Cours, Note
from inscriptions.models import Inscription
from emploi_temps.models import Salle, EmploiDuTemps

print("=== Suppression des anciennes données de test ===")

Note.objects.all().delete()
EmploiDuTemps.objects.all().delete()
Salle.objects.all().delete()
Inscription.objects.all().delete()
Cours.objects.all().delete()
Semestre.objects.all().delete()
AnneeAcademique.objects.all().delete()
Filiere.objects.all().delete()
Niveau.objects.all().delete()

# On supprime uniquement les comptes etudiant/enseignant (PAS les superutilisateurs admin)
Utilisateur.objects.filter(role__in=['etudiant', 'enseignant']).delete()

print("Anciennes données supprimées.\n")

print("=== Création des données académiques ===")

filiere_gi = Filiere.objects.create(nom_filiere="Génie Informatique", description="GI")
filiere_ig = Filiere.objects.create(nom_filiere="Informatique de Gestion", description="IG")

niveau_l1 = Niveau.objects.create(libelle="L1")
niveau_l2 = Niveau.objects.create(libelle="L2")
niveau_l3 = Niveau.objects.create(libelle="L3")
niveau_m1 = Niveau.objects.create(libelle="M1")
niveau_m2 = Niveau.objects.create(libelle="M2")

annee = AnneeAcademique.objects.create(
    libelle="2026-2027",
    date_debut=date(2026, 9, 1),
    date_fin=date(2027, 7, 31)
)

semestre1 = Semestre.objects.create(
    annee_academique=annee,
    libelle="Semestre 1",
    date_debut=date(2026, 9, 1),
    date_fin=date(2027, 1, 31)
)
semestre2 = Semestre.objects.create(
    annee_academique=annee,
    libelle="Semestre 2",
    date_debut=date(2027, 2, 1),
    date_fin=date(2027, 7, 31)
)

print("Données académiques créées.\n")

print("=== Création des enseignants ===")

def creer_enseignant(username, prenom, nom, matricule, specialite, grade):
    user = Utilisateur.objects.create_user(
        username=username,
        password="Test1234!",
        first_name=prenom,
        last_name=nom,
        role='enseignant'
    )
    return Enseignant.objects.create(
        utilisateur=user,
        matricule=matricule,
        specialite=specialite,
        grade=grade
    )

ens1 = creer_enseignant("enseignant1", "Moussa", "Poudiougo", "ENS001", "Programmation", "Maître assistant")
ens2 = creer_enseignant("enseignant2", "Aïcha", "Traoré", "ENS002", "Réseaux", "Maître de conférences")

print("2 enseignants créés (enseignant1, enseignant2 / mdp: Test1234!)\n")

print("=== Création des étudiants ===")

def creer_etudiant(username, prenom, nom, matricule, date_naissance, lieu):
    user = Utilisateur.objects.create_user(
        username=username,
        password="Test1234!",
        first_name=prenom,
        last_name=nom,
        role='etudiant'
    )
    return Etudiant.objects.create(
        utilisateur=user,
        matricule=matricule,
        date_naissance=date_naissance,
        lieu_naissance=lieu
    )

etu1 = creer_etudiant("etudiant1", "Oumou", "Niangaly", "ETU001", date(2004, 4, 15), "Koro")
etu2 = creer_etudiant("etudiant2", "Ibrahim", "Coulibaly", "ETU002", date(2003, 6, 20), "Bamako")
etu3 = creer_etudiant("etudiant3", "Fatoumata", "Diarra", "ETU003", date(2004, 1, 10), "Sikasso")
etu4 = creer_etudiant("etudiant4", "Seydou", "Keita", "ETU004", date(2003, 11, 5), "Kayes")

print("4 étudiants créés (etudiant1 à etudiant4 / mdp: Test1234!)\n")

print("=== Création des cours ===")

cours1 = Cours.objects.create(
    intitule="Programmation Orientée Objet",
    credits=4,
    filiere=filiere_gi,
    niveau=niveau_l2,
    semestre=semestre1,
    enseignant=ens1
)
cours2 = Cours.objects.create(
    intitule="Réseaux Informatiques",
    credits=3,
    filiere=filiere_gi,
    niveau=niveau_l2,
    semestre=semestre1,
    enseignant=ens2
)

print("2 cours créés (POO, Réseaux) en L2 GI\n")

print("=== Création des inscriptions (toutes validées) ===")

for etu in [etu1, etu2, etu3, etu4]:
    Inscription.objects.create(
        etudiant=etu,
        filiere=filiere_gi,
        niveau=niveau_l2,
        annee_academique=annee,
        statut='VALIDEE'
    )

print("4 inscriptions validées créées (L2 GI, 2026-2027)\n")

print("=== Création de la salle et de l'emploi du temps ===")

salle_a101 = Salle.objects.create(nom="Salle A101", capacite=40)

EmploiDuTemps.objects.create(
    cours=cours1, enseignant=ens1, salle=salle_a101,
    jour_semaine='LUNDI', heure_debut=time(8, 0), heure_fin=time(10, 0)
)
EmploiDuTemps.objects.create(
    cours=cours2, enseignant=ens2, salle=salle_a101,
    jour_semaine='MERCREDI', heure_debut=time(10, 0), heure_fin=time(12, 0)
)

print("Salle et 2 créneaux créés.\n")

print("=== Création de quelques notes ===")

Note.objects.create(etudiant=etu1, cours=cours1, valeur=15.5, type_evaluation='EXAMEN', date_evaluation=date(2026, 12, 10))
Note.objects.create(etudiant=etu2, cours=cours1, valeur=12.0, type_evaluation='EXAMEN', date_evaluation=date(2026, 12, 10))
Note.objects.create(etudiant=etu1, cours=cours2, valeur=17.0, type_evaluation='DS', date_evaluation=date(2026, 11, 5))

print("3 notes créées.\n")

print("=== TERMINÉ ===")
print("Comptes de test disponibles (mot de passe : Test1234!) :")
print("  Enseignants : enseignant1 (POO), enseignant2 (Réseaux)")
print("  Étudiants   : etudiant1, etudiant2, etudiant3, etudiant4 (tous en L2 GI, inscrits et validés)")