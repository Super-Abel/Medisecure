import os
import django
from datetime import date

# Initialisation de l'environnement Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from medisecure.medical.models import (
    Specialite,
    Cabinet,
    DossierMedical,
    SignesVitaux,
    Consultation,
    Prescription,
    ResultatAnalyse,
)
from medisecure.rdv.models import RendezVous, StatutRDV
from django.utils import timezone
from datetime import date, timedelta, datetime
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

    # 1b. Création de 2 Infirmiers
    for i in range(1, 3):
        email = f"nurse{i}@medisecure.com"
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "nom": f"Infirmier{i}",
                "prenom": f"Soin{i}",
                "role": Roles.INFIRMIER,
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
            EmailAddress.objects.get_or_create(
                user=user, email=email, defaults={"verified": True, "primary": True}
            )
            print(f"Infirmier créé : {email}")

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

    # 4. Création de Signes Vitaux pour les dossiers médicaux
    print("\nCréation des signes vitaux...")
    dossiers = DossierMedical.objects.all()
    if dossiers.exists():
        for dossier in dossiers:
            # Créer 2 entrées de constantes par patient
            for j in range(2):
                SignesVitaux.objects.create(
                    dossier=dossier,
                    poids=70 + i + j,
                    taille=170 + i,
                    temperature=36.5 + j,
                    tension_systolique=120 + j * 5,
                    tension_diastolique=80 + j * 2,
                    frequence_cardiaque=70 + j * 2,
                    saturation_oxygene=98 + j,
                    observations=f"Constantes de routine {j+1}/2",
                )
        print("Signes vitaux créés.")

    # 5. Création de Consultations
    print("\nCréation des consultations...")
    if dossiers.exists() and medecins.exists():
        for i, dossier in enumerate(dossiers):
            Consultation.objects.create(
                dossier=dossier,
                medecin=medecins[i % medecins.count()],
                date_consult=timezone.now() - timedelta(days=5),
                diagnostic=(
                    "Infection respiratoire mineure"
                    if i % 2 == 0
                    else "Suivi hypertension"
                ),
                observations="Patient réactif au traitement.",
            )
        print("Consultations créées.")

    # 6. Création de Prescriptions
    print("\nCréation des prescriptions...")
    if dossiers.exists() and medecins.exists():
        for i, dossier in enumerate(dossiers):
            Prescription.objects.create(
                dossier=dossier,
                medecin=medecins[i % medecins.count()],
                medicament="Amoxicilline" if i % 2 == 0 else "Lisinopril",
                dosage="500mg" if i % 2 == 0 else "10mg",
                posologie=(
                    "1 comprimé 3 fois par jour"
                    if i % 2 == 0
                    else "1 comprimé le matin"
                ),
                date_debut=date.today() - timedelta(days=5),
                date_fin=date.today() + timedelta(days=5),
                is_active=True,
            )
        print("Prescriptions créées.")

    # 7. Création de Résultats d'Analyses
    print("\nCréation des résultats d'analyses...")
    if dossiers.exists():
        for dossier in dossiers:
            ResultatAnalyse.objects.create(
                dossier=dossier,
                examen="Glycémie à jeun",
                valeur="0.95",
                unite="g/L",
                norme="0.70 - 1.10",
                statut="Normal",
                date_examen=timezone.now() - timedelta(days=10),
            )
        print("Résultats d'analyses créés.")

    print("\nSeeding terminé avec succès !")
    print(f"Mot de passe pour tous les comptes : {password}")


if __name__ == "__main__":
    seed_data()
