from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    email = serializers.EmailField()
    nom = serializers.CharField()
    prenom = serializers.CharField()
    role = serializers.CharField()
    statut = serializers.BooleanField()


from rest_framework import serializers


class PatientRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    nom = serializers.CharField()
    prenom = serializers.CharField()
    telephone = serializers.CharField(required=False, allow_blank=True)
    date_naissance = serializers.DateField(required=False, allow_null=True)
    sexe = serializers.CharField(required=False, allow_blank=True)
    adresse = serializers.CharField(required=False, allow_blank=True)


class MedecinRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    nom = serializers.CharField()
    prenom = serializers.CharField()
    telephone = serializers.CharField(required=False, allow_blank=True)
    numero_licence = serializers.CharField()
    specialite_id = serializers.IntegerField()
    cabinet_id = serializers.IntegerField(required=False, allow_null=True)


class NurseRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    nom = serializers.CharField()
    prenom = serializers.CharField()
    telephone = serializers.CharField(required=False, allow_blank=True)
