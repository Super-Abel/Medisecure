import os
import sys
import django

# Force UTF-8 output on Windows
if sys.stdout.encoding != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from datetime import date, timedelta
from allauth.account.models import EmailAddress
from medisecure.users.models import Roles, Patient, Medecin
from medisecure.medical.models import (
    Specialite, Cabinet, DossierMedical,
    SignesVitaux, Consultation, Prescription, ResultatAnalyse,
)
from medisecure.rdv.models import RendezVous, StatutRDV

User = get_user_model()
PASSWORD = "demo_password123"
NOW = timezone.now()


# ─── helpers ───────────────────────────────────────────────────────────────────
def make_user(email, nom, prenom, role, telephone=""):
    user, created = User.objects.get_or_create(
        email=email,
        defaults=dict(nom=nom, prenom=prenom, role=role,
                      telephone=telephone, is_active=True, statut=True),
    )
    if created:
        user.set_password(PASSWORD)
        user.save()
        EmailAddress.objects.get_or_create(
            user=user, email=email,
            defaults={"verified": True, "primary": True},
        )
    else:
        user.nom = nom; user.prenom = prenom
        user.is_active = True; user.statut = True
        user.save()
    return user, created


def rdv(patient, medecin, delta_days, delta_hours=10,
        motif="Consultation de suivi", statut=StatutRDV.CONFIRME, notes=""):
    RendezVous.objects.get_or_create(
        patient=patient, medecin=medecin,
        date_heure=NOW + timedelta(days=delta_days, hours=delta_hours),
        defaults=dict(motif=motif, statut=statut, notes=notes, duree=30),
    )


def consult(dossier, medecin, delta_days, diagnostic, observations):
    Consultation.objects.create(
        dossier=dossier, medecin=medecin,
        date_consult=NOW - timedelta(days=delta_days),
        diagnostic=diagnostic, observations=observations,
    )


def prescription(dossier, medecin, medicament, dosage, posologie,
                 debut_days_ago=5, duree=10, active=True):
    Prescription.objects.create(
        dossier=dossier, medecin=medecin,
        medicament=medicament, dosage=dosage, posologie=posologie,
        date_debut=date.today() - timedelta(days=debut_days_ago),
        date_fin=date.today() + timedelta(days=duree),
        is_active=active,
    )


def labo(dossier, examen, valeur, unite, norme, statut, delta_days=10):
    ResultatAnalyse.objects.create(
        dossier=dossier, examen=examen, valeur=valeur,
        unite=unite, norme=norme, statut=statut,
        date_examen=NOW - timedelta(days=delta_days),
    )


def signes(dossier, infirmier, poids, taille, temp,
           sys, dia, fc, spo2, obs, delta_days=0):
    SignesVitaux.objects.create(
        dossier=dossier, infirmier=infirmier,
        poids=poids, taille=taille, temperature=temp,
        tension_systolique=sys, tension_diastolique=dia,
        frequence_cardiaque=fc, saturation_oxygene=spo2,
        observations=obs,
        created_at=NOW - timedelta(days=delta_days),
    )


# ─── RESET ─────────────────────────────────────────────────────────────────────
def reset():
    print("[reset] Nettoyage...")
    with transaction.atomic():
        emails_to_keep = {"admin@demo.com"}
        Medecin.objects.all().delete()
        Patient.objects.all().delete()
        User.objects.exclude(email__in=emails_to_keep).delete()


# ─── SEED ──────────────────────────────────────────────────────────────────────
def seed():
    reset()
    print("[seed] Demarrage...\n")

    # ── Spécialités ────────────────────────────────────────────────────────────
    specs = {}
    for nom, desc in [
        ("Médecine Générale",   "Suivi global et médecine de premier recours"),
        ("Cardiologie",         "Maladies du cœur et des vaisseaux"),
        ("Neurologie",          "Maladies du système nerveux"),
        ("Dermatologie",        "Maladies de la peau"),
        ("Pédiatrie",           "Médecine de l'enfant"),
    ]:
        s, _ = Specialite.objects.get_or_create(
            nom_specialite=nom, defaults={"description": desc}
        )
        specs[nom] = s

    # ── Cabinets ────────────────────────────────────────────────────────────────
    cabinets = {}
    for nom, adresse, tel in [
        ("Clinique du Wouri",        "12 Av. du Général de Gaulle, Douala",  "+237 233 420 100"),
        ("Polyclinique de Yaoundé",  "45 Rue Nachtigal, Yaoundé",            "+237 222 230 200"),
        ("Centre Médical Akwa",      "3 Bd de la Liberté, Douala-Akwa",      "+237 233 410 050"),
    ]:
        c, _ = Cabinet.objects.get_or_create(
            nom=nom, defaults={"adresse": adresse, "telephone": tel}
        )
        cabinets[nom] = c

    # ── Médecins ────────────────────────────────────────────────────────────────
    MEDECINS_DATA = [
        ("doctor1@medisecure.com", "Diallo",    "Amadou",    "MED-CM-001", "Médecine Générale", "Clinique du Wouri",       "+237 699 100 001"),
        ("doctor2@medisecure.com", "Mvondo",    "Christiane","MED-CM-002", "Cardiologie",        "Polyclinique de Yaoundé", "+237 699 100 002"),
        ("doctor3@medisecure.com", "Essono",    "Pierre",    "MED-CM-003", "Neurologie",         "Centre Médical Akwa",     "+237 699 100 003"),
        ("doctor4@medisecure.com", "Ngono",     "Béatrice",  "MED-CM-004", "Dermatologie",       "Clinique du Wouri",       "+237 699 100 004"),
        ("doctor5@medisecure.com", "Kamga",     "Rodrigue",  "MED-CM-005", "Pédiatrie",          "Polyclinique de Yaoundé", "+237 699 100 005"),
    ]
    medecins = []
    for email, nom, prenom, lic, spec_nom, cab_nom, tel in MEDECINS_DATA:
        user, _ = make_user(email, nom, prenom, Roles.MEDECIN, tel)
        m, _ = Medecin.objects.get_or_create(user=user)
        m.numero_licence = lic
        m.specialite = specs[spec_nom]
        m.cabinet = cabinets[cab_nom]
        m.save()
        medecins.append(m)
        print(f"  👨‍⚕️  Dr {prenom} {nom} ({spec_nom})")

    # ── Infirmiers ──────────────────────────────────────────────────────────────
    INFIRMIERS_DATA = [
        ("nurse1@medisecure.com", "Ateba",  "Sandrine", "+237 699 200 001"),
        ("nurse2@medisecure.com", "Fouda",  "Bertrand", "+237 699 200 002"),
    ]
    infirmiers = []
    for email, nom, prenom, tel in INFIRMIERS_DATA:
        user, _ = make_user(email, nom, prenom, Roles.INFIRMIER, tel)
        infirmiers.append(user)
        print(f"  🩺  Infirmier·e {prenom} {nom}")

    # ── Patients ────────────────────────────────────────────────────────────────
    PATIENTS_DATA = [
        # email, nom, prenom, tel, naissance, sexe, groupe, poids, taille, adresse, antecedents, allergies, traitements
        (
            "patient1@medisecure.com", "Bah", "Aminata", "+237 677 300 001",
            date(1985, 3, 14), "F", "A+", 62.0, 165,
            "Rue des Flamboyants, Akwa, Douala",
            "Hypertension artérielle (depuis 2018), appendicectomie (2010)",
            "Pénicilline (urticaire), Aspirine (allergie digestive)",
            "Amlodipine 5mg/j, Ramipril 10mg/j",
        ),
        (
            "patient2@medisecure.com", "Nguyen", "Kévin", "+237 677 300 002",
            date(1992, 7, 22), "M", "O+", 78.5, 178,
            "Quartier Bastos, Yaoundé",
            "Diabète type 2 (depuis 2020), fracture cheville droite (2015)",
            "Sulfamides",
            "Metformine 1000mg 2x/j, Atorvastatine 20mg/j",
        ),
        (
            "patient3@medisecure.com", "Fofana", "Mariam", "+237 677 300 003",
            date(1978, 11, 5), "F", "B-", 55.0, 162,
            "Avenue Kennedy, Yaoundé",
            "Asthme bronchique (depuis l'enfance), rhinite allergique",
            "Ibuprofène, Aspirine",
            "Salbutamol inhaler, Béclométasone 200µg/j",
        ),
        (
            "patient4@medisecure.com", "Dubois", "Luc", "+237 677 300 004",
            date(2010, 1, 30), "M", "AB+", 32.0, 135,
            "Cité Verte, Yaoundé",
            "Aucun antécédent notable",
            "Aucune allergie connue",
            "Aucun traitement en cours",
        ),
        (
            "patient5@medisecure.com", "Kadem", "Yasmine", "+237 677 300 005",
            date(1995, 9, 18), "F", "A-", 58.0, 168,
            "Bonamoussadi, Douala",
            "Migraine chronique (depuis 2019), trouble anxieux",
            "Codéine",
            "Sumatriptan 50mg (si crise), Escitalopram 10mg/j",
        ),
    ]
    patients = []
    dossiers = []
    for (email, nom, prenom, tel, naiss, sexe, grp, poids, taille,
         adresse, antec, aller, traitement) in PATIENTS_DATA:
        user, _ = make_user(email, nom, prenom, Roles.PATIENT, tel)
        pat, _ = Patient.objects.get_or_create(
            user=user,
            defaults=dict(
                date_naissance=naiss, sexe=sexe, groupe_sanguin=grp,
                poids=poids, taille=taille, adresse=adresse,
            ),
        )
        pat.date_naissance = naiss; pat.sexe = sexe
        pat.groupe_sanguin = grp; pat.poids = poids
        pat.taille = taille; pat.adresse = adresse
        pat.save()
        dos, _ = DossierMedical.objects.get_or_create(patient=pat)
        dos.antecedents = antec
        dos.allergies   = aller
        dos.traitements = traitement
        dos.save()
        patients.append(pat)
        dossiers.append(dos)
        print(f"  👤  {prenom} {nom} ({grp})")

    # Raccourcis nommés
    p1,p2,p3,p4,p5 = patients
    d1,d2,d3,d4,d5 = dossiers
    m1,m2,m3,m4,m5 = medecins          # MedGen, Cardio, Neuro, Dermato, Pédiatre
    inf1, inf2 = infirmiers

    print("\n📅 Rendez-vous…")
    # ── Passés (TERMINE) ────────────────────────────────────────────────────────
    rdv(p1, m1, -30, motif="Suivi hypertension",           statut=StatutRDV.TERMINE)
    rdv(p1, m2, -15, motif="Bilan cardiaque annuel",       statut=StatutRDV.TERMINE)
    rdv(p2, m1, -20, motif="Suivi diabète type 2",         statut=StatutRDV.TERMINE)
    rdv(p2, m2, -10, motif="Échocardiographie de contrôle",statut=StatutRDV.TERMINE)
    rdv(p3, m1, -25, motif="Crise d'asthme — urgence",    statut=StatutRDV.TERMINE)
    rdv(p3, m3, -8,  motif="Céphalées persistantes",       statut=StatutRDV.TERMINE)
    rdv(p4, m5, -14, motif="Vaccin rappel DTP",            statut=StatutRDV.TERMINE)
    rdv(p5, m3, -12, motif="Migraine réfractaire",         statut=StatutRDV.TERMINE)
    rdv(p5, m1, -5,  motif="Renouvellement ordonnance",    statut=StatutRDV.TERMINE)

    # ── Aujourd'hui / très prochains (CONFIRME) ──────────────────────────────
    rdv(p1, m1,  0,  motif="Contrôle tension artérielle",  statut=StatutRDV.CONFIRME,
        notes="Apporter résultats labo du mois dernier")
    rdv(p2, m1,  1,  motif="Renouvellement Metformine",    statut=StatutRDV.CONFIRME)
    rdv(p3, m4,  2,  motif="Consultation dermatologie — eczéma", statut=StatutRDV.CONFIRME)
    rdv(p4, m5,  3,  motif="Visite de croissance 13 ans",  statut=StatutRDV.CONFIRME,
        notes="Prévoir bilan sanguin pédiatrique")
    rdv(p5, m3,  1,  motif="IRM résultats — bilan neuro",  statut=StatutRDV.CONFIRME)

    # ── À venir (EN_ATTENTE) ─────────────────────────────────────────────────
    rdv(p1, m4,  7,  motif="Lésion cutanée à examiner",   statut=StatutRDV.EN_ATTENTE)
    rdv(p2, m3, 10,  motif="Paresthésies membres inférieurs", statut=StatutRDV.EN_ATTENTE)
    rdv(p3, m1, 14,  motif="Bilan général annuel",         statut=StatutRDV.EN_ATTENTE)
    rdv(p5, m4, 21,  motif="Acné — suivi dermatologie",   statut=StatutRDV.EN_ATTENTE)

    # ── Annulés ──────────────────────────────────────────────────────────────
    rdv(p2, m4, -3,  motif="Consultation peau",            statut=StatutRDV.ANNULE,
        notes="Patient a annulé la veille")

    print("💬 Consultations…")
    # ── Patient 1 : Aminata — HTA ────────────────────────────────────────────
    consult(d1, m1, 30,
            "Hypertension artérielle stade 1",
            "PA 148/92 mmHg. Patient bien tolérante au traitement. Adaptation posologie Amlodipine à 5mg.")
    consult(d1, m2, 15,
            "Bilan cardiaque : absence d'atteinte organique",
            "ECG normal, pas d'hypertrophie ventriculaire. Échocardiographie satisfaisante. Poursuite traitement actuel.")

    # ── Patient 2 : Kévin — Diabète ──────────────────────────────────────────
    consult(d2, m1, 20,
            "Diabète type 2 — déséquilibre glycémique",
            "HbA1c à 8,2 % (cible < 7 %). Majoration Metformine 1500mg/j. Régime diabétique renforcé.")
    consult(d2, m2, 10,
            "Surveillance cardiovasculaire chez diabétique",
            "Léger souffle aortique. Surveillance annuelle. Atorvastatine maintenue. Cholestérol LDL 1,15 g/L.")

    # ── Patient 3 : Mariam — Asthme ──────────────────────────────────────────
    consult(d3, m1, 25,
            "Asthme bronchique — exacerbation modérée",
            "DEP 68 % valeur théorique. Corticoïde systémique 5 jours. Renforcement béclométasone.")
    consult(d3, m3, 8,
            "Bilan céphalées — migraine sans aura probable",
            "RAS à l'examen neurologique. IRM cerveau programmée. Sumatriptan introduit si crise.")

    # ── Patient 4 : Luc — Pédiatrie ──────────────────────────────────────────
    consult(d4, m5, 14,
            "Croissance normale pour l'âge",
            "Poids P50, taille P60. Développement psychomoteur adapté. Vaccin DTP administré. RAS.")

    # ── Patient 5 : Yasmine — Migraine ───────────────────────────────────────
    consult(d5, m3, 12,
            "Migraine chronique avec aura — traitement de fond",
            "3 crises/mois en moyenne. Introduction Escitalopram 10mg pour comorbidité anxieuse. Sumatriptan efficace.")
    consult(d5, m1, 5,
            "Renouvellement ordonnances migraine et anxiété",
            "Bonne tolérance Escitalopram. Crises ramenées à 1/mois. Poursuivre traitement 6 mois.")

    print("💊 Prescriptions…")
    # ── Patient 1 ─────────────────────────────────────────────────────────────
    prescription(d1, m1, "Amlodipine",  "5mg",  "1 comprimé le matin",        debut_days_ago=30, duree=60)
    prescription(d1, m1, "Ramipril",    "10mg", "1 comprimé le soir au repas", debut_days_ago=30, duree=60)
    prescription(d1, m2, "Aspirine",    "100mg","1 comprimé le matin (protection cardiovasculaire)", debut_days_ago=15, duree=90)

    # ── Patient 2 ─────────────────────────────────────────────────────────────
    prescription(d2, m1, "Metformine",     "1000mg","1 comprimé matin et soir au repas", debut_days_ago=20, duree=30)
    prescription(d2, m1, "Atorvastatine",  "20mg",  "1 comprimé le soir",               debut_days_ago=20, duree=90)
    prescription(d2, m2, "Aspirine",       "75mg",  "1 comprimé le matin",              debut_days_ago=10, duree=180)

    # ── Patient 3 ─────────────────────────────────────────────────────────────
    prescription(d3, m1, "Salbutamol",      "100µg/dose","2 bouffées si besoin (max 8/j)", debut_days_ago=25, duree=60)
    prescription(d3, m1, "Béclométasone",   "200µg",     "2 bouffées matin et soir",       debut_days_ago=25, duree=90)
    prescription(d3, m1, "Prednisone",      "40mg",      "1 comprimé/j pendant 5 jours",   debut_days_ago=8,  duree=5, active=False)

    # ── Patient 4 ─────────────────────────────────────────────────────────────
    prescription(d4, m5, "Vitamine D3",  "1000 UI","1 goutte/j pendant 3 mois", debut_days_ago=14, duree=90)
    prescription(d4, m5, "Paracétamol",  "250mg",  "1 suppositoire si fièvre > 38,5°C",  debut_days_ago=14, duree=30)

    # ── Patient 5 ─────────────────────────────────────────────────────────────
    prescription(d5, m3, "Sumatriptan",   "50mg", "1 comprimé dès le début de la crise (max 2/24h)", debut_days_ago=12, duree=60)
    prescription(d5, m3, "Escitalopram",  "10mg", "1 comprimé le matin",                              debut_days_ago=12, duree=180)
    prescription(d5, m1, "Paracétamol",  "1000mg","1 comprimé toutes les 6h si douleur",             debut_days_ago=5,  duree=7)

    print("🔬 Résultats d'analyses…")
    # ── Patient 1 — HTA ───────────────────────────────────────────────────────
    labo(d1, "Créatinine",          "90",    "µmol/L", "60-110",         "Normal",   30)
    labo(d1, "Potassium",           "4.1",   "mmol/L", "3.5-5.0",        "Normal",   30)
    labo(d1, "Cholestérol total",   "2.10",  "g/L",    "< 2.00",         "Élevé",    15)
    labo(d1, "NFS — Hémoglobine",   "12.8",  "g/dL",   "12.0-16.0 (F)", "Normal",   15)

    # ── Patient 2 — Diabète ───────────────────────────────────────────────────
    labo(d2, "HbA1c",               "8.2",   "%",      "< 7.0",          "Élevé",    20)
    labo(d2, "Glycémie à jeun",     "1.65",  "g/L",    "0.70-1.10",      "Élevé",    20)
    labo(d2, "LDL Cholestérol",     "1.15",  "g/L",    "< 1.30 (diabète)","Normal",  10)
    labo(d2, "Créatinine",          "82",    "µmol/L", "60-110",         "Normal",   10)
    labo(d2, "Microalbuminurie",    "18",    "mg/L",   "< 20",           "Normal",   10)

    # ── Patient 3 — Asthme ────────────────────────────────────────────────────
    labo(d3, "EFR — VEMS",          "72",    "% théorique","> 80 %",     "Altéré",   25)
    labo(d3, "EFR — CVF",           "85",    "% théorique","> 80 %",     "Normal",   25)
    labo(d3, "IgE totales",         "420",   "UI/mL",  "< 100",          "Élevé",    25)
    labo(d3, "NFS — Éosinophiles",  "650",   "/mm³",   "< 500",          "Élevé",    25)

    # ── Patient 4 — Pédiatrie ─────────────────────────────────────────────────
    labo(d4, "NFS complète",        "Normal","",       "",               "Normal",   14)
    labo(d4, "Vitamine D",          "18",    "ng/mL",  "20-60",          "Insuffisant",14)
    labo(d4, "Ferritine",           "22",    "µg/L",   "15-150",         "Normal",   14)

    # ── Patient 5 — Migraine ─────────────────────────────────────────────────
    labo(d5, "IRM cérébrale",       "Sans anomalie significative","","","Normal",    12)
    labo(d5, "TSH",                 "2.1",   "mUI/L",  "0.4-4.0",        "Normal",   12)
    labo(d5, "NFS — Hémoglobine",   "11.9",  "g/dL",   "12.0-16.0 (F)", "Bas",      12)
    labo(d5, "Ferritine",           "8",     "µg/L",   "15-150",         "Bas",       5)

    print("📊 Signes vitaux…")
    # ── Patient 1 ─────────────────────────────────────────────────────────────
    signes(d1, inf1, 62.0, 165, 36.7, 148, 92, 76, 98, "HTA non contrôlée à l'arrivée",          30)
    signes(d1, inf1, 62.0, 165, 36.5, 136, 84, 72, 99, "Après adaptation traitement — amélioration", 15)
    signes(d1, inf2, 62.5, 165, 36.6, 132, 82, 70, 99, "Contrôle à J+15 — stable",                  0)

    # ── Patient 2 ─────────────────────────────────────────────────────────────
    signes(d2, inf1, 78.5, 178, 36.8, 125, 80, 80, 98, "Glycémie 1,65 g/L à l'arrivée",           20)
    signes(d2, inf2, 77.0, 178, 36.6, 122, 78, 78, 98, "Poids stabilisé après régime",             10)

    # ── Patient 3 ─────────────────────────────────────────────────────────────
    signes(d3, inf1, 55.0, 162, 37.2, 118, 75, 92, 94, "Dyspnée modérée — saturation basse",       25)
    signes(d3, inf2, 55.0, 162, 36.8, 116, 74, 84, 97, "Post-traitement — amélioration nette",       8)

    # ── Patient 4 ─────────────────────────────────────────────────────────────
    signes(d4, inf1, 32.0, 135, 36.5, 100, 65, 82, 99, "Constantes pédiatriques normales",         14)

    # ── Patient 5 ─────────────────────────────────────────────────────────────
    signes(d5, inf2, 58.0, 168, 36.9, 115, 72, 78, 98, "Migraine en cours à l'arrivée",            12)
    signes(d5, inf1, 58.0, 168, 36.6, 112, 70, 72, 99, "Après Sumatriptan — résolution crise",      5)

    print("\n✅ Seeding terminé !")
    print(f"\nMot de passe : {PASSWORD}\n")
    print("Comptes disponibles :")
    print("  Admin    : admin@demo.com")
    for (email, nom, prenom, *_) in MEDECINS_DATA:
        print(f"  Médecin  : {email}  (Dr {prenom} {nom})")
    for (email, nom, prenom, *_) in INFIRMIERS_DATA:
        print(f"  Infirmier: {email}  ({prenom} {nom})")
    for (email, nom, prenom, *_) in PATIENTS_DATA:
        print(f"  Patient  : {email}  ({prenom} {nom})")


if __name__ == "__main__":
    seed()
