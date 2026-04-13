from rest_framework import serializers
from .models import Specialite, Cabinet, DossierMedical, Prescription, Consultation, ResultatAnalyse


class SpecialiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialite
        fields = "__all__"


class CabinetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cabinet
        fields = "__all__"


class DossierMedicalSerializer(serializers.ModelSerializer):
    class Meta:
        model = DossierMedical
        fields = "__all__"


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
