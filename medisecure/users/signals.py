from django.db.models.signals import post_save
from django.dispatch import receiver
from medisecure.users.models import User, Roles, Patient, Medecin
from medisecure.medical.models import DossierMedical


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.role == Roles.PATIENT:
            patient = Patient.objects.create(user=instance)
            DossierMedical.objects.get_or_create(patient=patient)
        elif instance.role == Roles.MEDECIN:
            Medecin.objects.get_or_create(user=instance)
