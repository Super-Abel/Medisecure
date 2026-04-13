import os
import django
from datetime import date

# Initialisation de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from medisecure.medical.models import Specialite, Cabinet, DossierMedical
from medisecure.rdv.models import RendezVous, StatutRDV
from django.utils import timezone
from datetime import date, timedelta
from django.db import transaction
from allauth.account.models import EmailAddress
from medisecure.users.models import Roles, Patient, Medecin

User = get_user_model()


def seed_data():
    print("Nettoyage des anciennes données de test...")
    with transaction.atomic():
        # Clean up ALL medecins and patients to avoid unique constraint issues
        Medecin.objects.all().delete()
        Patient.objects.all().delete()

        # Keep only the main admin if it exists
        User.objects.exclude(email="admin@demo.com").delete()

    print("Démarrage du seeding...")

    # Création d'une spécialité et d'un cabinet par défaut
    spec, _ = Specialite.objects.get_or_create(
        nom_specialite="Médecine Générale",
        defaults={"description": "Suivi global du patient"},
    )
    cab, _ = Cabinet.objects.get_or_create(
        nom="Centre Médical MediSecure",
        defaults={"adresse": "10 Rue de la Paix, Douala"},
    )

    password = "demo_password123"

    # 1. Création de 5 Docteurs
    for i in range(1, 6):
        email = f"doctor{i}@medisecure.com"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "nom": f"Docteur{i}",
                "prenom": f"Mederic{i}",
                "role": Roles.MEDECIN,
                "is_active": True,
                "statut": True,
            },
        )
        user.is_active = True
        user.statut = True
        user.save()
        if created:
            user.set_password(password)
            user.save()
            # Mark email as verified for allauth
            EmailAddress.objects.get_or_create(
                user=user, email=email, defaults={"verified": True, "primary": True}
            )

            lic = f"LIC-00{i}"
            print(f"Assignation de la licence {lic} pour {email}...")

            # Use get_or_create because a signal might have already created a profile with an empty licence
            medecin, _ = Medecin.objects.get_or_create(user=user)
            medecin.numero_licence = lic
            medecin.specialite = spec
            medecin.cabinet = cab
            medecin.save()
            print(f"Docteur créé/mis à jour : {email}")

    # 2. Création de 5 Patients
    for i in range(1, 6):
        email = f"patient{i}@medisecure.com"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "nom": f"Patient{i}",
                "prenom": f"Jean{i}",
                "role": Roles.PATIENT,
                "is_active": True,
                "statut": True,
            },
        )
        user.is_active = True
        user.statut = True
        user.save()
        if created:
            user.set_password(password)
            user.save()
            # Mark email as verified for allauth
            EmailAddress.objects.get_or_create(
                user=user, email=email, defaults={"verified": True, "primary": True}
            )

            patient_profile, _ = Patient.objects.get_or_create(
                user=user,
                defaults={
                    "date_naissance": date(1990 + i, 1, 1),
                    "adresse": f"{i} bis rue des Tests",
                },
            )
            # Create medical record
            DossierMedical.objects.get_or_create(patient=patient_profile)
            print(f"Patient créé : {email}")

    # 3. Création de quelques Rendez-vous
    print("\nCréation des rendez-vous...")
    patients = Patient.objects.all()
    medecins = Medecin.objects.all()
    if patients.exists() and medecins.exists():
        for i in range(3):
            RendezVous.objects.get_or_create(
                patient=patients[i % patients.count()],
                medecin=medecins[i % medecins.count()],
                date_heure=timezone.now() + timedelta(days=i + 1, hours=10),
                defaults={
                    "motif": "Consultation de routine",
                    "statut": StatutRDV.CONFIRME,
                },
            )
        print("Rendez-vous créés.")

    print("\nSeeding terminé avec succès !")
    print(f"Mot de passe pour tous les comptes : {password}")


if __name__ == "__main__":
    seed_data()
