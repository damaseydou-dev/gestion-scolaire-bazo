from django.contrib import admin
from django.core.mail import send_mail
from .models import Inscription


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'telephone_inscription', 'filiere', 'niveau', 'annee_academique', 'statut')
    list_filter = ('statut', 'filiere', 'annee_academique')
    search_fields = ('etudiant__matricule', 'telephone_inscription', 'etudiant__utilisateur__first_name')
    list_editable = ('statut',)

    def save_model(self, request, obj, form, change):
        """Envoie un email à l'étudiant quand son statut change (y compris via list_editable)."""
        ancien_statut = None
        if change and obj.pk:
            ancien_statut = Inscription.objects.get(pk=obj.pk).statut

        super().save_model(request, obj, form, change)

        # On envoie l'email seulement si le statut vient de changer
        if ancien_statut != obj.statut:
            email_destinataire = obj.etudiant.utilisateur.email
            if not email_destinataire:
                return  # pas d'email renseigné, on ignore silencieusement

            prenom = obj.etudiant.utilisateur.first_name or "Cher étudiant"

            if obj.statut == 'VALIDEE':
                send_mail(
                    subject="Inscription validée - Université BAZO",
                    message=(
                        f"Bonjour {prenom},\n\n"
                        f"Votre inscription en {obj.filiere.nom_filiere} ({obj.niveau.libelle}) "
                        f"pour l'année {obj.annee_academique} a été validée par l'administration.\n\n"
                        f"Cordialement,\nUniversité BAZO"
                    ),
                    from_email=None,
                    recipient_list=[email_destinataire],
                    fail_silently=True,
                )
            elif obj.statut == 'REJETEE':
                send_mail(
                    subject="Inscription non retenue - Université BAZO",
                    message=(
                        f"Bonjour {prenom},\n\n"
                        f"Votre demande d'inscription en {obj.filiere.nom_filiere} ({obj.niveau.libelle}) "
                        f"pour l'année {obj.annee_academique} n'a pas été retenue. "
                        f"Merci de contacter l'administration pour plus d'informations.\n\n"
                        f"Cordialement,\nUniversité BAZO"
                    ),
                    from_email=None,
                    recipient_list=[email_destinataire],
                    fail_silently=True,
                )