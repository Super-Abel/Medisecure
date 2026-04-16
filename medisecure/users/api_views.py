from drf_spectacular.utils import extend_schema
from rest_framework import status, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenRefreshView as SimpleJWTTokenRefreshView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import User
from medisecure.users.repositories import DjangoUserRepository, DjangoLogRepository
from medisecure.application.auth_service import AuthService
from .serializers import LoginSerializer, UserSerializer


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(APIView):
    authentication_classes = []
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

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        # Vérification du mot de passe via Django auth
        django_user = authenticate(request, username=email, password=password)
        if django_user is None:
            return Response(
                {"detail": "Email ou mot de passe incorrect."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        user = service.login(email=email, ip_address=request.META.get("REMOTE_ADDR"))

        if not user:
            return Response(
                {"detail": "Compte inactif ou non vérifié."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(django_user)
        return Response(
            {
                "access_token": str(refresh.access_token),
                "refresh_token": str(refresh),
                "token_type": "bearer",
                "role": user.role.value,
                "user_id": user.id_utilisateur,
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


@method_decorator(csrf_exempt, name="dispatch")
class ForgotPasswordView(APIView):
    authentication_classes = []
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


@method_decorator(csrf_exempt, name="dispatch")
class ResetPasswordView(APIView):
    authentication_classes = []
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


@method_decorator(csrf_exempt, name="dispatch")
class PatientRegistrationView(APIView):
    authentication_classes = []
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
        patient = Patient.objects.create(
            user=user,
            date_naissance=d.get("date_naissance"),
            sexe=d.get("sexe", ""),
            adresse=d.get("adresse", ""),
        )
        from medisecure.medical.models import DossierMedical

        DossierMedical.objects.create(patient=patient)
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


@method_decorator(csrf_exempt, name="dispatch")
class MedecinRegistrationView(APIView):
    authentication_classes = []
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


@method_decorator(csrf_exempt, name="dispatch")
class NurseRegistrationView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        request=globals().get("NurseRegistrationSerializer", None),
        responses={201: UserSerializer},
        summary="S'inscrire en tant qu'infirmier",
        tags=["Auth"],
    )
    def post(self, request):
        from .serializers import NurseRegistrationSerializer
        from .models import User
        from medisecure.domain.models import LogEntity

        ser = NurseRegistrationSerializer(data=request.data)
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
            role="INFIRMIER",
        )
        service = AuthService(DjangoUserRepository(), DjangoLogRepository())
        service.send_verification_email(user.id, user.email)

        DjangoLogRepository().record(
            LogEntity(
                None, user.id, "Inscription Infirmier", request.META.get("REMOTE_ADDR")
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


@method_decorator(csrf_exempt, name="dispatch")
class VerifyEmailView(APIView):
    authentication_classes = []
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


class CustomTokenRefreshView(SimpleJWTTokenRefreshView):
    """
    Vue personnalisée pour rafraîchir le token.
    Permet de passer le refresh token dans le header Authorization: Bearer <token>
    au lieu du corps de la requête.
    """

    @extend_schema(
        request=None,
        responses={200: dict},
        summary="Rafraîchir le token JWT (via Header Authorization)",
        tags=["Auth"],
    )
    def post(self, request, *args, **kwargs):
        # Si le refresh token n'est pas dans le body, on le cherche dans le header Authorization
        if "refresh" not in request.data:
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                refresh_token = auth_header.split(" ")[1]
                # On injecte le token dans les données pour le sérialiseur SimpleJWT
                request.data._mutable = True
                request.data["refresh"] = refresh_token
                request.data._mutable = False

        try:
            return super().post(request, *args, **kwargs)
        except (InvalidToken, TokenError) as e:
            raise InvalidToken(e.args[0])


class PatientMeProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={200: None},
        summary="Consulter mon profil patient (Mobile)",
        tags=["Profils"],
    )
    def get(self, request):
        if not hasattr(request.user, "patient_profile"):
            return Response({"detail": "Profil patient introuvable."}, status=404)
        p = request.user.patient_profile
        return Response(
            {
                "id": p.id,
                "user_id": request.user.id,
                "email": request.user.email,
                "nom": request.user.nom,
                "prenom": request.user.prenom,
                "date_naissance": p.date_naissance,
                "sexe": p.sexe,
                "adresse": p.adresse,
                "groupe_sanguin": p.groupe_sanguin,
            }
        )


class PatientCreateByNurseSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    prenom = serializers.CharField()
    nom = serializers.CharField()
    telephone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["email", "password", "prenom", "nom", "telephone"]

    def create(self, validated_data):
        from .models import Roles, User, Patient

        validated_data["role"] = Roles.PATIENT
        validated_data["statut"] = True  # Auto-verify
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        Patient.objects.create(user=user)
        return user


class NurseCreatePatientView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        request=PatientCreateByNurseSerializer,
        responses={201: PatientCreateByNurseSerializer},
        summary="Enregistrer un nouveau patient (par une infirmière)",
        tags=["Auth"],
    )
    def post(self, request):
        from .models import Roles

        if request.user.role != Roles.INFIRMIER:
            return Response(
                {"error": "Seul un infirmier peut créer un patient"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PatientCreateByNurseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
