from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from medisecure.medical.repositories import (
    DjangoSpecialiteRepository,
    DjangoCabinetRepository,
    DjangoDossierMedicalRepository,
)
from medisecure.application.medical_service import MedicalService
from medisecure.application.dossier_service import DossierMedicalService
from medisecure.domain.models import DossierMedicalEntity
from .serializers import (
    SpecialiteSerializer,
    CabinetSerializer,
    DossierMedicalSerializer,
    DossierMedicalCreateSerializer,
    PrescriptionSerializer,
    ConsultationSerializer,
    ResultatAnalyseSerializer,
)
from .models import Prescription, Consultation, ResultatAnalyse


class SpecialiteListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: SpecialiteSerializer(many=True)},
        summary="Lister les spécialités médicales",
        tags=["Médical"],
    )
    def get(self, request):
        service = MedicalService(
            DjangoSpecialiteRepository(), DjangoCabinetRepository()
        )
        return Response(
            [
                {
                    "id": s.id_specialite,
                    "nom_specialite": s.nom_specialite,
                    "description": s.description,
                }
                for s in service.list_specialites()
            ]
        )


class CabinetListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        responses={200: CabinetSerializer(many=True)},
        summary="Lister les cabinets",
        tags=["Médical"],
    )
    def get(self, request):
        service = MedicalService(
            DjangoSpecialiteRepository(), DjangoCabinetRepository()
        )
        return Response(
            [
                {
                    "id": c.id_cabinet,
                    "nom": c.nom,
                    "adresse": c.adresse,
                    "telephone": c.telephone,
                }
                for c in service.list_cabinets()
            ]
        )


class DossierMedicalView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: DossierMedicalSerializer, 404: None},
        summary="Récupérer le dossier médical d'un patient",
        tags=["Dossier Médical"],
    )
    def get(self, request, patient_id=None):
        service = DossierMedicalService(DjangoDossierMedicalRepository())

        # Gestion de l'alias 'my' pour le mobile
        if patient_id is None:
            if hasattr(request.user, "patient_profile"):
                patient_id = request.user.patient_profile.id
            else:
                return Response({"detail": "Vous n'êtes pas un patient."}, status=403)

        dossier = service.get_patient_dossier(patient_id)
        if not dossier:
            return Response(
                {"detail": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(
            {
                "id_dossier": dossier.id_dossier,
                "patient_id": dossier.patient_id,
                "antecedents": dossier.antecedents,
                "allergies": dossier.allergies,
                "traitements": dossier.traitements,
            }
        )

    @extend_schema(
        request=DossierMedicalCreateSerializer,
        responses={200: DossierMedicalSerializer},
        summary="Sauvegarder / mettre à jour un dossier médical (chiffré AES-256)",
        tags=["Dossier Médical"],
    )
    def post(self, request, patient_id: int):
        serializer = DossierMedicalCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        service = DossierMedicalService(DjangoDossierMedicalRepository())
        dossier = service.save_dossier(
            DossierMedicalEntity(
                id_dossier=None,
                patient_id=patient_id,
                antecedents=data["antecedents"],
                allergies=data["allergies"],
                traitements=data["traitements"],
            )
        )
        return Response(
            {"id_dossier": dossier.id_dossier, "patient_id": dossier.patient_id}
        )


class MedicalBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if getattr(user, "role", "") == "PATIENT":
            return self.queryset.filter(dossier__patient__user=user)
        elif getattr(user, "role", "") == "MEDECIN" and hasattr(
            self.queryset.model, "medecin"
        ):
            return self.queryset.filter(medecin__user=user)
        return self.queryset.all()


class PrescriptionViewSet(MedicalBaseViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionSerializer


class ConsultationViewSet(MedicalBaseViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer


class ResultatAnalyseViewSet(MedicalBaseViewSet):
    queryset = ResultatAnalyse.objects.all()
    serializer_class = ResultatAnalyseSerializer
