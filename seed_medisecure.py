import os
import django
from datetime import date

# Initialisation de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model
from medisecure.users.models import Roles, Patient, Medecin
from medisecure.medical.models import Specialite, Cabinet
from allauth.account.models import EmailAddress

User = get_user_model()


def seed_data():
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
            },
        )
        if created:
            user.set_password(password)
            user.save()
            # Mark email as verified for allauth
            EmailAddress.objects.get_or_create(
                user=user, email=email, defaults={"verified": True, "primary": True}
            )

            Medecin.objects.create(
                user=user, specialite=spec, cabinet=cab, numero_licence=f"LIC-00{i}"
            )
            print(f"Docteur créé : {email}")

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
            },
        )
        if created:
            user.set_password(password)
            user.save()
            # Mark email as verified for allauth
            EmailAddress.objects.get_or_create(
                user=user, email=email, defaults={"verified": True, "primary": True}
            )

            Patient.objects.create(
                user=user,
                date_naissance=date(1990 + i, 1, 1),
                adresse=f"{i} bis rue des Tests",
            )
            print(f"Patient créé : {email}")

    print("\nSeeding terminé avec succès !")
    print(f"Mot de passe pour tous les comptes : {password}")


if __name__ == "__main__":
    seed_data()
