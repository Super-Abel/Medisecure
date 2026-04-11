from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import RendezVousService
from .entities import RendezVousEntity
from .serializers import (
    RendezVousSerializer,
    RendezVousCreateSerializer,
    RendezVousUpdateSerializer,
)


class PatientRDVListView(APIView):
    """UC004 - Consulter - Réserver"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: RendezVousSerializer(many=True)},
        summary="Consulter ses rendez-vous",
        tags=["Rendez-vous"],
    )
    def get(self, request, patient_id: int):
        svc = RendezVousService()
        rdvs = svc.list_by_patient(patient_id)
        return Response(
            [
                {
                    "id_rdv": r.id_rdv,
                    "patient_id": r.patient_id,
                    "medecin_id": r.medecin_id,
                    "date_heure": r.date_heure,
                    "motif": r.motif,
                    "statut": r.statut,
                }
                for r in rdvs
            ]
        )

    @extend_schema(
        request=RendezVousCreateSerializer,
        responses={201: RendezVousSerializer},
        summary="Réserver un rendez-vous",
        tags=["Rendez-vous"],
    )
    def post(self, request, patient_id: int):
        ser = RendezVousCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        svc = RendezVousService()
        rdv = svc.reserver(
            RendezVousEntity(
                id_rdv=None,
                patient_id=patient_id,
                medecin_id=d["medecin_id"],
                date_heure=d["date_heure"],
                motif=d["motif"],
            )
        )
        return Response(
            {"id_rdv": rdv.id_rdv, "statut": rdv.statut}, status=status.HTTP_201_CREATED
        )


class MedecinPlanningView(APIView):
    """UC008 - Consulter le planning médecin"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: RendezVousSerializer(many=True)},
        summary="Consulter le planning d'un médecin",
        tags=["Rendez-vous"],
    )
    def get(self, request, medecin_id: int):
        svc = RendezVousService()
        rdvs = svc.list_by_medecin(medecin_id)
        return Response(
            [
                {
                    "id_rdv": r.id_rdv,
                    "patient_id": r.patient_id,
                    "medecin_id": r.medecin_id,
                    "date_heure": r.date_heure,
                    "motif": r.motif,
                    "statut": r.statut,
                }
                for r in rdvs
            ]
        )


class RDVDetailView(APIView):
    """UC006 - Annuler / UC007 - Modifier"""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: RendezVousSerializer, 404: None},
        summary="Consulter un rendez-vous",
        tags=["Rendez-vous"],
    )
    def get(self, request, rdv_id: int):
        from .models import RendezVous
        try:
            rdv = RendezVous.objects.get(id=rdv_id)
        except RendezVous.DoesNotExist:
            return Response({"detail": "RDV introuvable."}, status=status.HTTP_404_NOT_FOUND)
        return Response({
            "id_rdv": rdv.id,
            "patient_id": rdv.patient_id,
            "medecin_id": rdv.medecin_id,
            "date_heure": rdv.date_heure,
            "motif": rdv.motif,
            "statut": rdv.statut,
        })

    @extend_schema(
        request=RendezVousUpdateSerializer,
        responses={200: RendezVousSerializer},
        summary="Modifier un rendez-vous",
        tags=["Rendez-vous"],
    )
    def patch(self, request, rdv_id: int):
        ser = RendezVousUpdateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data
        svc = RendezVousService()
        rdv = svc.modifier(rdv_id, date_heure=d.get("date_heure"), motif=d.get("motif"))
        if not rdv:
            return Response(
                {"detail": "RDV introuvable."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {"id_rdv": rdv.id_rdv, "statut": rdv.statut, "date_heure": rdv.date_heure}
        )

    @extend_schema(
        responses={200: RendezVousSerializer},
        summary="Annuler un rendez-vous",
        tags=["Rendez-vous"],
    )
    def delete(self, request, rdv_id: int):
        svc = RendezVousService()
        rdv = svc.annuler(rdv_id)
        if not rdv:
            return Response(
                {"detail": "RDV introuvable."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response({"id_rdv": rdv.id_rdv, "statut": rdv.statut})
