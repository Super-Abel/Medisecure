from rest_framework import serializers
from .models import RendezVous


class RendezVousSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = "__all__"


class RendezVousCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = ["patient", "medecin", "date_heure", "duree", "motif", "notes"]


class RendezVousUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RendezVous
        fields = ["date_heure", "duree", "motif", "notes", "statut"]
