from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .notifications import Notification
from .models import Patient, Medecin


# ========== Notifications ==========
class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None},
        summary="Consulter ses notifications",
        tags=["Notifications"],
    )
    def get(self, request):
        notifs = Notification.objects.filter(utilisateur=request.user)
        return Response(
            [
                {
                    "id": n.id,
                    "message": n.message,
                    "type": n.type,
                    "statut": n.statut,
                    "date_envoi": n.date_envoi,
                }
                for n in notifs
            ]
        )


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None},
        summary="Marquer une notification comme lue",
        tags=["Notifications"],
    )
    def patch(self, request, notif_id: int):
        try:
            notif = Notification.objects.get(id=notif_id, utilisateur=request.user)
            notif.statut = "LU"
            notif.save()
            return Response({"id": notif.id, "statut": notif.statut})
        except Notification.DoesNotExist:
            return Response(
                {"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND
            )


# ========== Profil Patient ==========
class PatientListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None},
        summary="Lister tous les patients (Admin)",
        tags=["Administration"],
    )
    def get(self, request):
        patients = Patient.objects.select_related("user").all()
        return Response(
            [
                {
                    "id": p.id,
                    "email": p.user.email,
                    "nom": p.user.nom,
                    "prenom": p.user.prenom,
                    "date_naissance": p.date_naissance,
                    "sexe": p.sexe,
                    "adresse": p.adresse,
                }
                for p in patients
            ]
        )


class PatientDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None}, summary="Consulter un profil patient", tags=["Patients"]
    )
    def get(self, request, patient_id: int):
        try:
            p = Patient.objects.select_related("user").get(id=patient_id)
            return Response(
                {
                    "id": p.id,
                    "email": p.user.email,
                    "nom": p.user.nom,
                    "prenom": p.user.prenom,
                    "date_naissance": p.date_naissance,
                    "sexe": p.sexe,
                    "adresse": p.adresse,
                }
            )
        except Patient.DoesNotExist:
            return Response(
                {"detail": "Introuvable."}, status=status.HTTP_404_NOT_FOUND
            )


# ========== Profil Médecin ==========
class MedecinListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None}, summary="Lister tous les médecins", tags=["Médecins"]
    )
    def get(self, request):
        medecins = Medecin.objects.select_related("user", "specialite", "cabinet").all()
        return Response(
            [
                {
                    "id": m.id,
                    "email": m.user.email,
                    "nom": m.user.nom,
                    "prenom": m.user.prenom,
                    "numero_licence": m.numero_licence,
                    "specialite": m.specialite.nom_specialite if m.specialite else None,
                    "cabinet": m.cabinet.nom if m.cabinet else None,
                }
                for m in medecins
            ]
        )
