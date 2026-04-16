from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from medisecure.medical.models import Specialite, Cabinet
from .managers import UserManager
from django.utils import timezone


class Roles(models.TextChoices):
    PATIENT = "PATIENT", _("Patient")
    MEDECIN = "MEDECIN", _("Médecin")
    INFIRMIER = "INFIRMIER", _("Infirmier")
    ADMIN = "ADMIN", _("Administrateur")


class User(AbstractUser):
    # Fields from Schema.sql
    role = models.CharField(
        max_length=15,
        choices=Roles.choices,
        default=Roles.PATIENT,
    )
    nom = models.CharField(_("Nom"), blank=True, max_length=100)
    prenom = models.CharField(_("Prénom"), blank=True, max_length=100)
    telephone = models.CharField(_("Téléphone"), blank=True, max_length=20)
    statut = models.BooleanField(default=False)  # False until email is verified
    failed_attempts = models.IntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)

    name = None  # Use nom/prenom instead
    first_name = None  # type: ignore[assignment]
    last_name = None  # type: ignore[assignment]
    email = models.EmailField(_("email address"), unique=True)
    username = None  # type: ignore[assignment]

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["nom", "prenom"]

    objects: ClassVar[UserManager] = UserManager()

    def __str__(self):
        return self.email

    def get_absolute_url(self) -> str:
        return reverse("users:detail", kwargs={"pk": self.id})


class Patient(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="patient_profile"
    )
    date_naissance = models.DateField(null=True, blank=True)
    sexe = models.CharField(max_length=10, blank=True)
    adresse = models.TextField(blank=True)
    groupe_sanguin = models.CharField(max_length=5, blank=True)
    poids = models.FloatField(null=True, blank=True)
    taille = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"Patient: {self.user.email}"


class Medecin(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="medecin_profile"
    )
    specialite = models.ForeignKey(
        Specialite,
        on_delete=models.PROTECT,
        related_name="medecins",
        null=True,  # Temporaire pour faciliter la migration si des médecins existent déjà
    )
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.SET_NULL,
        related_name="medecins",
        null=True,
        blank=True,
    )
    numero_licence = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return f"Médecin: {self.user.email}"


class Admin(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="admin_profile"
    )
    niveau_acces = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return f"Admin: {self.user.email}"


class LogActivite(models.Model):
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logs")
    action = models.TextField()
    date_action = models.DateTimeField(auto_now_add=True)
    adresse_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.date_action} - {self.utilisateur.email}: {self.action[:30]}"


class PasswordResetToken(models.Model):
    utilisateur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="reset_tokens"
    )
    token = models.UUIDField(
        default=__import__("uuid").uuid4, unique=True, editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self) -> bool:
        from django.utils import timezone

        return not self.used and (timezone.now() - self.created_at).seconds < 3600

    def __str__(self):
        return f"Reset token for {self.utilisateur.email} ({'used' if self.used else 'valid'})"


def generate_otp():
    import random

    return str(random.randint(100000, 999999))


class EmailVerificationToken(models.Model):
    utilisateur = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="verification_tokens"
    )
    token = models.UUIDField(
        default=__import__("uuid").uuid4, unique=True, editable=False
    )
    otp = models.CharField(max_length=6, default=generate_otp)
    created_at = models.DateTimeField(auto_now_add=True)
    used = models.BooleanField(default=False)

    def is_valid(self) -> bool:
        from django.utils import timezone
        from datetime import timedelta

        return not self.used and self.created_at >= timezone.now() - timedelta(hours=48)


class Disponibilite(models.Model):
    medecin = models.ForeignKey(
        Medecin, on_delete=models.CASCADE, related_name="disponibilites"
    )
    date_specifique = models.DateField(default=timezone.now)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    class Meta:
        unique_together = ("medecin", "date_specifique")
        ordering = ["date_specifique"]

    def __str__(self):
        return f"{self.medecin.user.email} - {self.date_specifique} ({self.heure_debut} -> {self.heure_fin})"
