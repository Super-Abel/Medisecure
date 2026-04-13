from rest_framework import serializers
from medisecure.users.models import User, Patient, Medecin


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = [
            "date_naissance",
            "sexe",
            "adresse",
            "groupe_sanguin",
            "poids",
            "taille",
        ]


class MedecinSerializer(serializers.ModelSerializer):
    specialite_nom = serializers.ReadOnlyField(source="specialite.nom_specialite")
    cabinet_nom = serializers.ReadOnlyField(source="cabinet.nom")

    # Write-only fields to allow creating new ones
    specialite_name = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )
    cabinet_name = serializers.CharField(
        write_only=True, required=False, allow_blank=True
    )

    class Meta:
        model = Medecin
        fields = [
            "specialite",
            "specialite_nom",
            "specialite_name",
            "cabinet",
            "cabinet_nom",
            "cabinet_name",
            "numero_licence",
        ]

    def update(self, instance, validated_data):
        from medisecure.medical.models import Specialite, Cabinet

        spec_name = validated_data.pop("specialite_name", None)
        cab_name = validated_data.pop("cabinet_name", None)

        if spec_name:
            specialite, _ = Specialite.objects.get_or_create(nom_specialite=spec_name)
            instance.specialite = specialite

        if cab_name:
            cabinet, _ = Cabinet.objects.get_or_create(nom=cab_name)
            instance.cabinet = cabinet

        return super().update(instance, validated_data)


class UserSerializer(serializers.ModelSerializer[User]):
    patient_profile = PatientSerializer(required=False, allow_null=True)
    medecin_profile = MedecinSerializer(required=False, allow_null=True)

    class Meta:
        model = User
        fields = [
            "id",
            "nom",
            "prenom",
            "email",
            "telephone",
            "role",
            "url",
            "statut",
            "failed_attempts",
            "locked_until",
            "last_login",
            "date_joined",
            "patient_profile",
            "medecin_profile",
        ]
        read_only_fields = [
            "id",
            "email",
            "role",
            "url",
            "statut",
            "failed_attempts",
            "locked_until",
            "last_login",
            "date_joined",
        ]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "pk"},
        }

    def update(self, instance, validated_data):
        patient_data = validated_data.pop("patient_profile", None)
        medecin_data = validated_data.pop("medecin_profile", None)

        instance = super().update(instance, validated_data)

        if patient_data and hasattr(instance, "patient_profile"):
            p_ser = PatientSerializer(
                instance.patient_profile, data=patient_data, partial=True
            )
            p_ser.is_valid(raise_exception=True)
            p_ser.save()

        if medecin_data and hasattr(instance, "medecin_profile"):
            m_ser = MedecinSerializer(
                instance.medecin_profile, data=medecin_data, partial=True
            )
            m_ser.is_valid(raise_exception=True)
            m_ser.save()

        return instance
