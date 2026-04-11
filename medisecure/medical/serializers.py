from rest_framework import serializers


class SpecialiteSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom_specialite = serializers.CharField()
    description = serializers.CharField(allow_blank=True)


class CabinetSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    nom = serializers.CharField()
    adresse = serializers.CharField(allow_blank=True)
    telephone = serializers.CharField(allow_blank=True)


class DossierMedicalSerializer(serializers.Serializer):
    id_dossier = serializers.IntegerField()
    patient_id = serializers.IntegerField()
    antecedents = serializers.CharField(allow_blank=True)
    allergies = serializers.CharField(allow_blank=True)
    traitements = serializers.CharField(allow_blank=True)


class DossierMedicalCreateSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    antecedents = serializers.CharField(allow_blank=True, default="")
    allergies = serializers.CharField(allow_blank=True, default="")
    traitements = serializers.CharField(allow_blank=True, default="")
