from rest_framework import serializers
from .models import (
    Specialite,
    Cabinet,
    DossierMedical,
    Prescription,
    Consultation,
    ResultatAnalyse,
    SignesVitaux,
)


class SpecialiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialite
        fields = "__all__"


class CabinetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinet
        fields = "__all__"


class PrescriptionMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = [
            "id",
            "id_prescription",
            "medicament",
            "dosage",
            "posologie",
            "date_debut",
            "date_fin",
            "is_active",
            "created_at",
        ]

    id_prescription = serializers.IntegerField(source="id", read_only=True)


class ConsultationMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = [
            "id",
            "id_consultation",
            "date_consult",
            "diagnostic",
            "observations",
            "created_at",
        ]

    id_consultation = serializers.IntegerField(source="id", read_only=True)


class SignesVitauxSerializer(serializers.ModelSerializer):
    class Meta:
        model = SignesVitaux
        fields = "__all__"


class LabResultMobileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultatAnalyse
        fields = ["id", "examen", "valeur", "unite", "norme", "statut", "date_examen"]


class DossierMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedical
        fields = "__all__"


class DossierMedicalMobileSerializer(serializers.ModelSerializer):
    patient_id = serializers.IntegerField(source="patient.id", read_only=True)
    prescriptions = PrescriptionMobileSerializer(many=True, read_only=True)
    consultations = ConsultationMobileSerializer(many=True, read_only=True)
    lab_results = LabResultMobileSerializer(
        source="resultats_labo", many=True, read_only=True
    )

    patient = serializers.IntegerField(source="patient.id", read_only=True)
    resultats_labo = LabResultMobileSerializer(many=True, read_only=True)
    signes_vitaux = SignesVitauxSerializer(many=True, read_only=True)

    class Meta:
        model = DossierMedical
        fields = [
            "id",
            "id_dossier",
            "patient_id",
            "patient",
            "antecedents",
            "allergies",
            "traitements",
            "notes_medecin",
            "date_creation",
            "prescriptions",
            "consultations",
            "lab_results",
            "resultats_labo",
            "signes_vitaux",
        ]

    id_dossier = serializers.IntegerField(source="id", read_only=True)


class DossierMedicalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedical
        fields = ["patient", "antecedents", "allergies", "traitements", "notes_medecin"]


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = "__all__"


class ConsultationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Consultation
        fields = "__all__"


class ResultatAnalyseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResultatAnalyse
        fields = "__all__"
