from django.db import models
from django.utils.translation import gettext_lazy as _


class StatutRDV(models.TextChoices):
    EN_ATTENTE = "EN_ATTENTE", _("En attente")
    CONFIRME = "CONFIRME", _("Confirmé")
    ANNULE = "ANNULE", _("Annulé")
    TERMINE = "TERMINE", _("Terminé")


class RendezVous(models.Model):
    patient = models.ForeignKey(
        "users.Patient", on_delete=models.CASCADE, related_name="rdv"
    )
    medecin = models.ForeignKey(
        "users.Medecin", on_delete=models.CASCADE, related_name="rdv"
    )
    date_heure = models.DateTimeField()
    duree = models.IntegerField(_("Durée en minutes"), default=30)
    motif = models.CharField(max_length=255, blank=True)
    notes = models.TextField(_("Notes"), blank=True)
    statut = models.CharField(
        max_length=20, choices=StatutRDV.choices, default=StatutRDV.EN_ATTENTE
    )
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date_heure"]

    def __str__(self):
        return f"RDV {self.patient} / {self.medecin} - {self.date_heure}"
