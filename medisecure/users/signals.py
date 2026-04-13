from django.db.models.signals import post_save
from django.dispatch import receiver
from medisecure.users.models import User, Roles, Patient, Medecin
from medisecure.medical.models import DossierMedical


import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    logger.info(f"Ensuring profile for user {instance.email} with role {instance.role}")
    if instance.role == Roles.PATIENT:
        patient, _ = Patient.objects.get_or_create(user=instance)
        DossierMedical.objects.get_or_create(patient=patient)
        logger.info(f"Patient profile ensured for {instance.email}")
    elif instance.role == Roles.MEDECIN:
        med, created_prof = Medecin.objects.get_or_create(
            user=instance, defaults={"numero_licence": f"LIC-{instance.id}"}
        )
        logger.info(
            f"Medecin profile ensured (created={created_prof}) for {instance.email}"
        )
