import os
import django
from django.utils import timezone
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from medisecure.users.models import User, Patient, Medecin, Roles
from medisecure.rdv.models import RendezVous, StatutRDV
from medisecure.medical.models import Specialite, Cabinet, DossierMedical

# create user
email = "patient@demo.com"
user, created = User.objects.get_or_create(
    email=email,
    defaults={
        "nom": "Demo",
        "prenom": "Jean",
        "role": Roles.PATIENT,
        "is_active": True,
    },
)
if created:
    user.set_password("demo1234")
    user.save()

# create profile
patient, _ = Patient.objects.get_or_create(user=user)

# create doctor
doc_email = "doctor@demo.com"
doc_user, _ = User.objects.get_or_create(
    email=doc_email,
    defaults={
        "nom": "Smith",
        "prenom": "John",
        "role": Roles.MEDECIN,
        "is_active": True,
    },
)
if _:
    doc_user.set_password("demo1234")
    doc_user.save()

spec, _ = Specialite.objects.get_or_create(nom_specialite="Cardiologie")
cabinet, _ = Cabinet.objects.get_or_create(nom="Centre Coeur")
medecin, _ = Medecin.objects.get_or_create(
    user=doc_user,
    defaults={"specialite": spec, "cabinet": cabinet, "numero_licence": "DOC12345"},
)

# create RDV
RendezVous.objects.create(
    patient=patient,
    medecin=medecin,
    date_heure=timezone.now() + timedelta(days=2),
    motif="Contrôle annuel",
    statut=StatutRDV.CONFIRME,
)

# create Dossier
DossierMedical.objects.get_or_create(
    patient=patient, defaults={"antecedents": "None", "allergies": "Pénicilline"}
)

print(f"Demo data created for {email}")
