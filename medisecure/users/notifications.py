from django.db import models
from django.utils.translation import gettext_lazy as _


class StatutNotif(models.TextChoices):
    ENVOYE = "ENVOYE", _("Envoyé")
    LU = "LU", _("Lu")


class Notification(models.Model):
    utilisateur = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="notifications"
    )
    message = models.TextField()
    type = models.CharField(max_length=50, blank=True)
    date_envoi = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(
        max_length=10, choices=StatutNotif.choices, default=StatutNotif.ENVOYE
    )

    class Meta:
        ordering = ["-date_envoi"]

    def __str__(self):
        return f"Notif [{self.statut}] -> {self.utilisateur.email}"
