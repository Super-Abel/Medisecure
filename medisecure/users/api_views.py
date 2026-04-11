from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from medisecure.users.repositories import DjangoUserRepository, DjangoLogRepository
from medisecure.application.auth_service import AuthService
from .serializers import LoginSerializer, UserSerializer


class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=LoginSerializer,
        responses={200: UserSerializer, 401: None},
        summary="Authentifier un utilisateur",
        tags=["Auth"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        user = service.login(
            email=serializer.validated_data["email"],
            ip_address=request.META.get("REMOTE_ADDR"),
        )

        if not user:
            return Response(
                {"detail": "Email introuvable."}, status=status.HTTP_401_UNAUTHORIZED
            )

        return Response(
            {
                "id": user.id_utilisateur,
                "email": user.email,
                "nom": user.nom,
                "prenom": user.prenom,
                "role": user.role.value,
                "statut": user.statut,
            }
        )


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={204: None}, summary="Déconnecter un utilisateur", tags=["Auth"]
    )
    def post(self, request):
        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        service.logout(
            user_id=request.user.id, ip_address=request.META.get("REMOTE_ADDR")
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"email": {"type": "string"}},
            }
        },
        responses={200: None, 404: None},
        summary="Demander une réinitialisation de mot de passe",
        tags=["Auth"],
    )
    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"detail": "Email requis."}, status=status.HTTP_400_BAD_REQUEST
            )
        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        token = service.forgot_password(email)
        if token is None:
            return Response(
                {"detail": "Email introuvable."}, status=status.HTTP_404_NOT_FOUND
            )
        return Response({"detail": "Email de réinitialisation envoyé."})


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "new_password": {"type": "string"},
                },
            }
        },
        responses={200: None, 400: None},
        summary="Réinitialiser le mot de passe via token",
        tags=["Auth"],
    )
    def post(self, request):
        token = request.data.get("token")
        new_password = request.data.get("new_password")
        if not token or not new_password:
            return Response(
                {"detail": "Token et mot de passe requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        success = service.reset_password(token=token, new_password=new_password)
        if not success:
            return Response(
                {"detail": "Token invalide ou expiré."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({"detail": "Mot de passe réinitialisé avec succès."})


class PatientRegistrationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=globals().get("PatientRegistrationSerializer", None),
        responses={201: UserSerializer},
        summary="S'inscrire en tant que patient",
        tags=["Auth"],
    )
    def post(self, request):
        from .serializers import PatientRegistrationSerializer
        from .models import User, Patient
        from medisecure.domain.models import LogEntity

        ser = PatientRegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        if User.objects.filter(email=d["email"]).exists():
            return Response(
                {"detail": "Email déjà utilisé."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=d["email"],
            password=d["password"],
            nom=d["nom"],
            prenom=d["prenom"],
            telephone=d.get("telephone", ""),
            role="PATIENT",
        )
        Patient.objects.create(
            user=user,
            date_naissance=d.get("date_naissance"),
            sexe=d.get("sexe", ""),
            adresse=d.get("adresse", ""),
        )
        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        service.send_verification_email(user.id, user.email)

        DjangoLogRepository().record(
            LogEntity(
                None, user.id, "Inscription Patient", request.META.get("REMOTE_ADDR")
            )
        )
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "detail": "Veuillez vérifier votre e-mail pour activer votre compte.",
            },
            status=status.HTTP_201_CREATED,
        )


class MedecinRegistrationView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=globals().get("MedecinRegistrationSerializer", None),
        responses={201: UserSerializer},
        summary="S'inscrire en tant que médecin",
        tags=["Auth"],
    )
    def post(self, request):
        from .serializers import MedecinRegistrationSerializer
        from .models import User, Medecin
        from medisecure.medical.models import Specialite, Cabinet
        from medisecure.domain.models import LogEntity

        ser = MedecinRegistrationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        if User.objects.filter(email=d["email"]).exists():
            return Response(
                {"detail": "Email déjà utilisé."}, status=status.HTTP_400_BAD_REQUEST
            )
        if Medecin.objects.filter(numero_licence=d["numero_licence"]).exists():
            return Response(
                {"detail": "Licence déjà utilisée."}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            email=d["email"],
            password=d["password"],
            nom=d["nom"],
            prenom=d["prenom"],
            telephone=d.get("telephone", ""),
            role="MEDECIN",
        )
        spec = Specialite.objects.filter(id=d["specialite_id"]).first()
        cab = (
            Cabinet.objects.filter(id=d.get("cabinet_id")).first()
            if d.get("cabinet_id")
            else None
        )

        Medecin.objects.create(
            user=user, specialite=spec, cabinet=cab, numero_licence=d["numero_licence"]
        )
        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        service.send_verification_email(user.id, user.email)

        DjangoLogRepository().record(
            LogEntity(
                None, user.id, "Inscription Médecin", request.META.get("REMOTE_ADDR")
            )
        )
        return Response(
            {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "detail": "Veuillez vérifier votre e-mail pour activer votre compte.",
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        parameters=[
            {"name": "token", "in": "query", "type": "string", "required": False}
        ],
        responses={200: None, 400: None},
        summary="Vérifier une adresse email (Lien)",
        tags=["Auth"],
    )
    def get(self, request):
        token = request.query_params.get("token")
        if not token:
            return Response(
                {"detail": "Token requis."}, status=status.HTTP_400_BAD_REQUEST
            )

        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        success = service.verify_email(token=token)
        if not success:
            return Response(
                {"detail": "Lien invalide ou expiré."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "detail": "Email vérifié avec succès. Vous pouvez maintenant vous connecter."
            }
        )

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {"otp": {"type": "string"}},
                "required": ["otp"],
            }
        },
        responses={200: None, 400: None},
        summary="Vérifier une adresse email (OTP)",
        tags=["Auth"],
    )
    def post(self, request):
        otp = request.data.get("otp")
        if not otp:
            return Response(
                {"detail": "Code OTP requis."}, status=status.HTTP_400_BAD_REQUEST
            )

        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        success = service.verify_email(otp=otp)
        if not success:
            return Response(
                {"detail": "Code invalide ou expiré."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                "detail": "Email vérifié avec succès. Vous pouvez maintenant vous connecter."
            }
        )
