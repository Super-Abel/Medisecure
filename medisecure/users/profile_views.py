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
                    "statut": "sent" if n.statut == "ENVOYE" else "read",
                    "statut_web": n.statut,
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

    def put(self, request, notif_id: int):
        return self.patch(request, notif_id)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None},
        summary="Marquer toutes les notifications comme lues",
        tags=["Notifications"],
    )
    def patch(self, request):
        notifs_updated = Notification.objects.filter(
            utilisateur=request.user, statut="ENVOYE"
        ).update(statut="LU")
        return Response(
            {"message": f"{notifs_updated} notifications marquées comme lues"}
        )

    def put(self, request):
        return self.patch(request)


class NotificationUnreadCountView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None},
        summary="Compter les notifications non lues",
        tags=["Notifications"],
    )
    def get(self, request):
        count = Notification.objects.filter(
            utilisateur=request.user, statut="ENVOYE"
        ).count()
        return Response({"count": count})


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
                    "user_id": m.user.id,
                    "user": {
                        "nom": m.user.nom,
                        "prenom": m.user.prenom,
                        "email": m.user.email,
                    },
                    "email": m.user.email,
                    "nom": m.user.nom,
                    "prenom": m.user.prenom,
                    "numero_licence": m.numero_licence,
                    "specialite": m.specialite.nom_specialite if m.specialite else None,
                    "specialty": (
                        {
                            "id": m.specialite.id,
                            "nom": m.specialite.nom_specialite,
                        }
                        if m.specialite
                        else None
                    ),
                    "cabinet": m.cabinet.nom if m.cabinet else None,
                }
                for m in medecins
            ]
        )


class AvailableSlotsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, medecin_id):
        from medisecure.rdv.models import RendezVous
        from medisecure.users.models import Disponibilite
        from medisecure.users.models import Medecin
        from datetime import datetime, timedelta, date as datetime_date

        date_str = request.query_params.get("date")
        if not date_str:
            return Response({"error": "Date requise"}, status=400)

        try:
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"error": "Format de date invalide"}, status=400)

        try:
            medecin = Medecin.objects.get(id=medecin_id)
        except Medecin.DoesNotExist:
            return Response({"error": "Médecin introuvable"}, status=404)

        try:
            dispo = Disponibilite.objects.get(
                medecin=medecin, date_specifique=target_date
            )
        except Disponibilite.DoesNotExist:
            # Fallback for demo: default to 09:00 - 17:00
            from datetime import time

            dispo = type(
                "obj", (object,), {"heure_debut": time(9, 0), "heure_fin": time(17, 0)}
            )

        # Récupérer les RDV déjà pris
        rdvs_pris = RendezVous.objects.filter(
            medecin=medecin, date_heure__date=target_date
        ).exclude(statut="ANNULE")

        heures_prises = [rdv.date_heure.strftime("%H:%M") for rdv in rdvs_pris]

        # Générer des slots toutes les 30 mins
        slots = []
        current = datetime.combine(target_date, dispo.heure_debut)
        end_time = datetime.combine(target_date, dispo.heure_fin)

        while current + timedelta(minutes=30) <= end_time:
            time_str = current.strftime("%H:%M")
            if not ("12:30" <= time_str < "14:00"):
                if time_str not in heures_prises:
                    slots.append(time_str)
            current += timedelta(minutes=30)

        if target_date == datetime_date.today():
            now_str = datetime.now().strftime("%H:%M")
            slots = [s for s in slots if s > now_str]

        return Response(slots, status=200)


class UpdateAvailabilityView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from medisecure.users.models import Disponibilite

        if not hasattr(request.user, "medecin_profile"):
            return Response({"error": "Vous n'êtes pas un médecin"}, status=403)

        date_specifique = request.data.get("date_specifique")
        heure_debut = request.data.get("heure_debut")
        heure_fin = request.data.get("heure_fin")

        if not date_specifique or not heure_debut or not heure_fin:
            return Response({"error": "Données incomplètes"}, status=400)

        dispo, created = Disponibilite.objects.update_or_create(
            medecin=request.user.medecin_profile,
            date_specifique=date_specifique,
            defaults={"heure_debut": heure_debut, "heure_fin": heure_fin},
        )
        return Response({"status": "success", "id": dispo.id})


# ========== Planning Médecin ==========
class PlanningRdvByDateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from medisecure.rdv.models import RendezVous
        from datetime import date as date_type

        date_str = request.query_params.get("date")
        try:
            from datetime import datetime

            target_date = (
                datetime.strptime(date_str, "%Y-%m-%d").date()
                if date_str
                else date_type.today()
            )
        except ValueError:
            target_date = date_type.today()

        if not hasattr(request.user, "medecin_profile"):
            return Response([], status=200)

        rdvs = (
            RendezVous.objects.filter(
                medecin=request.user.medecin_profile, date_heure__date=target_date
            )
            .select_related("patient__user")
            .order_by("date_heure")
        )

        return Response(
            [
                {
                    "id": r.id,
                    "heure": r.date_heure.strftime("%H:%M"),
                    "patient_nom": f"{r.patient.user.prenom} {r.patient.user.nom}",
                    "patient_id": r.patient.id,
                    "motif": getattr(r, "motif", "Consultation générale")
                    or "Consultation générale",
                    "statut": r.statut,
                }
                for r in rdvs
            ]
        )
