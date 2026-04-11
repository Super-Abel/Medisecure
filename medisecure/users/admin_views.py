from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from medisecure.users.models import LogActivite, User


class LogActiviteListView(APIView):
    """Consulter logs d'activité (Admin seulement)"""

    permission_classes = [IsAdminUser]

    @extend_schema(
        responses={200: None},
        summary="Consulter les logs d'activité (Admin)",
        tags=["Administration"],
    )
    def get(self, request):
        logs = LogActivite.objects.select_related("utilisateur").order_by(
            "-date_action"
        )[:100]
        return Response(
            [
                {
                    "id": log.id,
                    "utilisateur": log.utilisateur.email,
                    "action": log.action,
                    "adresse_ip": log.adresse_ip,
                    "date_action": log.date_action,
                }
                for log in logs
            ]
        )


class UserRoleUpdateView(APIView):
    """Attribuer rôles et permissions"""

    permission_classes = [IsAdminUser]

    @extend_schema(
        request=None,
        responses={200: None},
        summary="Changer le rôle d'un utilisateur",
        tags=["Administration"],
    )
    def patch(self, request, user_id: int):
        role = request.data.get("role")
        if role not in ["PATIENT", "MEDECIN", "ADMIN"]:
            return Response({"detail": "Rôle invalide."}, status=400)
        try:
            user = User.objects.get(id=user_id)
            user.role = role
            user.save()
            return Response({"id": user.id, "email": user.email, "role": user.role})
        except User.DoesNotExist:
            return Response({"detail": "Utilisateur introuvable."}, status=404)
