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
    notes_medecin = models.TextField(_("Notes du médecin"), blank=True)

    date_creation = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dossier de {self.patient.user.email}"


class Prescription(models.Model):
    dossier = models.ForeignKey(
        DossierMedical, on_delete=models.CASCADE, related_name="prescriptions"
    )
    medecin = models.ForeignKey("users.Medecin", on_delete=models.SET_NULL, null=True)
    medicament = models.CharField(max_length=200)
    dosage = models.CharField(max_length=100, blank=True)
    posologie = models.CharField(max_length=200, blank=True)
    date_debut = models.DateField(null=True, blank=True)
    date_fin = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription: {self.medicament} pour {self.dossier.patient.user.email}"


class Consultation(models.Model):
    dossier = models.ForeignKey(
        DossierMedical, on_delete=models.CASCADE, related_name="consultations"
    )
    medecin = models.ForeignKey("users.Medecin", on_delete=models.SET_NULL, null=True)
    date_consult = models.DateTimeField()
    diagnostic = models.TextField(blank=True)
    observations = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Consultation le {self.date_consult.strftime('%Y-%m-%d')} pour {self.dossier.patient.user.email}"


class ResultatAnalyse(models.Model):
    dossier = models.ForeignKey(
        DossierMedical, on_delete=models.CASCADE, related_name="resultats_labo"
    )
    examen = models.CharField(max_length=200)
    valeur = models.CharField(max_length=100, blank=True)
    unite = models.CharField(max_length=50, blank=True)
    norme = models.CharField(max_length=100, blank=True)
    statut = models.CharField(max_length=20, blank=True)
    date_examen = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Résultat {self.examen} pour {self.dossier.patient.user.email}"


class SignesVitaux(models.Model):
    dossier = models.ForeignKey(
        DossierMedical, on_delete=models.CASCADE, related_name="signes_vitaux"
    )
    infirmier = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={"role": "INFIRMIER"},
    )
    poids = models.FloatField(_("Poids (kg)"), null=True, blank=True)
    taille = models.IntegerField(_("Taille (cm)"), null=True, blank=True)
    tension_systolique = models.IntegerField(
        _("Tension Systolique"), null=True, blank=True
    )
    tension_diastolique = models.IntegerField(
        _("Tension Diastolique"), null=True, blank=True
    )
    temperature = models.FloatField(_("Température (°C)"), null=True, blank=True)
    frequence_cardiaque = models.IntegerField(
        _("Fréquence Cardiaque (bpm)"), null=True, blank=True
    )
    saturation_oxygene = models.IntegerField(
        _("Saturation O2 (%)"), null=True, blank=True
    )
    observations = models.TextField(_("Observations"), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Signes vitaux du {self.created_at.strftime('%Y-%m-%d')} pour {self.dossier.patient.user.email}"
