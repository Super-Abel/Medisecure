from django.db import models
from django.utils.translation import gettext_lazy as _


class Specialite(models.Model):
    nom_specialite = models.CharField(_("Nom de la spécialité"), max_length=100)
    description = models.TextField(_("Description"), blank=True)

    def __str__(self):
        return self.nom_specialite


class Cabinet(models.Model):
    nom = models.CharField(_("Nom du cabinet"), max_length=150)
    adresse = models.TextField(_("Adresse"), blank=True)
    telephone = models.CharField(_("Téléphone"), max_length=20, blank=True)

    def __str__(self):
        return self.nom


class DossierMedical(models.Model):
    # On lie au Patient (défini dans l'app users)
    patient = models.OneToOneField(
        "users.Patient", on_delete=models.CASCADE, related_name="dossier"
    )

    # Ces champs seront stockés sous forme de texte chiffré (BinaryField ou TextField)
    # Pour la démo, on utilise TextField pour stocker le base64 du chiffré
    antecedents = models.TextField(_("Antécédents"), blank=True)
    allergies = models.TextField(_("Allergies"), blank=True)
    traitements = models.TextField(_("Traitements"), blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dossier de {self.patient.user.email}"
