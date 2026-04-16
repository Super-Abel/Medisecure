from datetime import date
import io

from drf_spectacular.utils import extend_schema
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.http import HttpResponse

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
    DossierMedicalMobileSerializer,
    DossierMedicalCreateSerializer,
    PrescriptionSerializer,
    PrescriptionMobileSerializer,
    ConsultationSerializer,
    ConsultationMobileSerializer,
    ResultatAnalyseSerializer,
    LabResultMobileSerializer,
    SignesVitauxSerializer,
)
from .models import Prescription, Consultation, ResultatAnalyse, SignesVitaux


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
                    "id_specialite": s.id_specialite,
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
                    "id_cabinet": c.id_cabinet,
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
        # Gestion de l'alias 'my' pour le mobile
        if patient_id is None:
            if hasattr(request.user, "patient_profile"):
                patient_id = request.user.patient_profile.id
            else:
                return Response({"detail": "Vous n'êtes pas un patient."}, status=403)

        from .models import DossierMedical

        try:
            dossier_obj = DossierMedical.objects.get(patient__id=patient_id)
        except DossierMedical.DoesNotExist:
            return Response(
                {"detail": "Dossier introuvable."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response(DossierMedicalMobileSerializer(dossier_obj).data)

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

    def put(self, request, patient_id: int):
        return self.post(request, patient_id)


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

    def perform_create(self, serializer):
        # Injection automatique du dossier si on passe par les routes mobiles /records/<id>/...
        patient_id = self.kwargs.get("patient_id")
        if patient_id:
            from .models import DossierMedical

            dossier = DossierMedical.objects.get(patient__id=patient_id)
            serializer.save(dossier=dossier)
        else:
            serializer.save()


class PrescriptionViewSet(MedicalBaseViewSet):
    queryset = Prescription.objects.all()
    serializer_class = PrescriptionMobileSerializer  # Use mobile version for dual-keys


class ConsultationViewSet(MedicalBaseViewSet):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationMobileSerializer


class ResultatAnalyseViewSet(MedicalBaseViewSet):
    queryset = ResultatAnalyse.objects.all()
    serializer_class = LabResultMobileSerializer


class SignesVitauxViewSet(MedicalBaseViewSet):
    queryset = SignesVitaux.objects.all()
    serializer_class = SignesVitauxSerializer


class DossierPDFView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None},
        summary="Exporter le dossier médical en PDF",
        tags=["Dossier Médical"],
    )
    def get(self, request, patient_id=None):
        from .models import DossierMedical
        from medisecure.users.models import Patient

        if patient_id is None:
            if not hasattr(request.user, "patient_profile"):
                return Response({"detail": "Vous n'êtes pas un patient."}, status=403)
            patient_id = request.user.patient_profile.id

        try:
            patient = Patient.objects.select_related("user").get(id=patient_id)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient introuvable."}, status=404)

        # Vérification accès : patient lui-même, médecin, ou infirmier
        user = request.user
        is_patient = hasattr(user, "patient_profile") and user.patient_profile.id == patient_id
        is_medecin = hasattr(user, "medecin_profile")
        is_infirmier = user.role == "INFIRMIER"
        if not (is_patient or is_medecin or is_infirmier or user.is_staff):
            return Response({"detail": "Accès refusé."}, status=403)

        try:
            dossier = DossierMedical.objects.prefetch_related(
                "prescriptions", "consultations", "resultats_labo", "signes_vitaux"
            ).get(patient=patient)
        except DossierMedical.DoesNotExist:
            dossier = None

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle("title", parent=styles["Heading1"], fontSize=16, textColor=colors.HexColor("#0f766e"))
        h2_style = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#1e293b"))
        normal = styles["Normal"]

        story = []

        # En-tête
        story.append(Paragraph("MediSecure — Dossier Médical", title_style))
        story.append(Paragraph(f"Généré le {date.today().strftime('%d/%m/%Y')}", normal))
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e2e8f0")))
        story.append(Spacer(1, 0.4*cm))

        # Infos patient
        story.append(Paragraph("Informations personnelles", h2_style))
        p = patient.user
        infos = [
            ["Nom", f"{p.prenom} {p.nom}"],
            ["Email", p.email],
            ["Téléphone", p.telephone or "-"],
            ["Date de naissance", patient.date_naissance.strftime("%d/%m/%Y") if patient.date_naissance else "-"],
            ["Sexe", patient.sexe or "-"],
            ["Groupe sanguin", patient.groupe_sanguin or "-"],
            ["Poids / Taille", f"{patient.poids or '-'} kg / {patient.taille or '-'} cm"],
            ["Adresse", patient.adresse or "-"],
        ]
        t = Table(infos, colWidths=[5*cm, 12*cm])
        t.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("BACKGROUND", (0, 0), (-1, -1), colors.white),
            ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.5*cm))

        if dossier:
            # Antécédents & Allergies
            story.append(Paragraph("Antécédents & Allergies", h2_style))
            story.append(Paragraph(f"<b>Antécédents :</b> {dossier.antecedents or 'Aucun'}", normal))
            story.append(Paragraph(f"<b>Allergies :</b> {dossier.allergies or 'Aucune'}", normal))
            story.append(Paragraph(f"<b>Traitements :</b> {dossier.traitements or 'Aucun'}", normal))
            story.append(Spacer(1, 0.5*cm))

            # Prescriptions
            prescriptions = list(dossier.prescriptions.all())
            if prescriptions:
                story.append(Paragraph("Prescriptions", h2_style))
                rows = [["Médicament", "Dosage", "Posologie", "Du", "Au", "Active"]]
                for rx in prescriptions:
                    rows.append([
                        rx.medicament,
                        rx.dosage or "-",
                        rx.posologie or "-",
                        rx.date_debut.strftime("%d/%m/%Y") if rx.date_debut else "-",
                        rx.date_fin.strftime("%d/%m/%Y") if rx.date_fin else "-",
                        "Oui" if rx.is_active else "Non",
                    ])
                t = Table(rows, colWidths=[4*cm, 2.5*cm, 3.5*cm, 2.5*cm, 2.5*cm, 2*cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(t)
                story.append(Spacer(1, 0.5*cm))

            # Signes vitaux
            vitaux = list(dossier.signes_vitaux.order_by("-created_at")[:5])
            if vitaux:
                story.append(Paragraph("Signes Vitaux (5 derniers)", h2_style))
                rows = [["Date", "Poids", "TA", "T°", "FC", "SpO2"]]
                for sv in vitaux:
                    ta = f"{sv.tension_systolique or '-'}/{sv.tension_diastolique or '-'}"
                    rows.append([
                        sv.created_at.strftime("%d/%m/%Y"),
                        f"{sv.poids or '-'} kg",
                        ta,
                        f"{sv.temperature or '-'} °C",
                        f"{sv.frequence_cardiaque or '-'} bpm",
                        f"{sv.saturation_oxygene or '-'} %",
                    ])
                t = Table(rows, colWidths=[3*cm, 2.5*cm, 3*cm, 2.5*cm, 3*cm, 3*cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, -1), 9),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]))
                story.append(t)

        doc.build(story)
        buffer.seek(0)

        nom_fichier = f"dossier_{patient.user.nom}_{patient.user.prenom}_{date.today()}.pdf"
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{nom_fichier}"'
        return response
