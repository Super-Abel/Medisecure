import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model
from medisecure.users.models import Roles, Patient, Medecin
from medisecure.medical.models import Specialite, Cabinet
from datetime import date

User = get_user_model()


def create_users():
    # 1. Admin
    admin, created = User.objects.get_or_create(
        email="admin@demo.com",
        defaults={
            "nom": "Super",
            "prenom": "Admin",
            "role": Roles.ADMIN,
            "is_staff": True,
            "is_superuser": True,
            "statut": True,
        },
    )
    admin.is_active = True
    admin.statut = True
    admin.set_password("demo1234")
    admin.save()
    print("Admin user ready: admin@demo.com / demo1234")

    # 2. Patient
    patient_user, created = User.objects.get_or_create(
        email="patient@demo.com",
        defaults={
            "nom": "Dupont",
            "prenom": "Jean",
            "role": Roles.PATIENT,
            "statut": True,
        },
    )
    patient_user.is_active = True
    patient_user.statut = True
    patient_user.set_password("demo1234")
    patient_user.save()
    Patient.objects.get_or_create(
        user=patient_user,
        defaults={
            "date_naissance": date(1980, 5, 15),
            "telephone": "0601020304",
            "adresse": "123 Rue de la Santé, Paris",
        },
    )
    print("Patient user ready: patient@demo.com / demo1234")

    # 3. Doctor
    doctor_user, created = User.objects.get_or_create(
        email="doctor@demo.com",
        defaults={
            "nom": "Smith",
            "prenom": "John",
            "role": Roles.MEDECIN,
            "statut": True,
        },
    )
    doctor_user.is_active = True
    doctor_user.statut = True
    doctor_user.set_password("demo1234")
    doctor_user.save()

    specialite, _ = Specialite.objects.get_or_create(
        nom_specialite="Cardiologie", defaults={"description": "Coeur et vaisseaux"}
    )
    cabinet, _ = Cabinet.objects.get_or_create(
        nom="Cabinet Coeur Santé", defaults={"adresse": "45 Ave de la République"}
    )

    # Handle doctor profile update robustly due to auto-creation signals
    medecin_profile, _ = Medecin.objects.get_or_create(user=doctor_user)
    medecin_profile.specialite = specialite
    medecin_profile.cabinet = cabinet
    medecin_profile.numero_licence = "LIC-10012345678"
    medecin_profile.save()
    print("Doctor user ready: doctor@demo.com / demo1234")


if __name__ == "__main__":
    create_users()
    print("Done!")
