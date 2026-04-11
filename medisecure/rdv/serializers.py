from rest_framework import serializers


class RendezVousSerializer(serializers.Serializer):
    id_rdv = serializers.IntegerField()
    patient_id = serializers.IntegerField()
    medecin_id = serializers.IntegerField()
    date_heure = serializers.DateTimeField()
    motif = serializers.CharField(allow_blank=True)
    statut = serializers.CharField()


class RendezVousCreateSerializer(serializers.Serializer):
    patient_id = serializers.IntegerField()
    medecin_id = serializers.IntegerField()
    date_heure = serializers.DateTimeField()
    motif = serializers.CharField(allow_blank=True, default="")


class RendezVousUpdateSerializer(serializers.Serializer):
    date_heure = serializers.DateTimeField(required=False)
    motif = serializers.CharField(required=False, allow_blank=True)
