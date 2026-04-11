from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from medisecure.users.api.views import UserViewSet
from medisecure.users.api_views import (
    LoginView,
    LogoutView,
    ForgotPasswordView,
    ResetPasswordView,
    PatientRegistrationView,
    MedecinRegistrationView,
    VerifyEmailView,
)
from medisecure.users.admin_views import LogActiviteListView, UserRoleUpdateView
from medisecure.users.profile_views import (
    NotificationListView,
    NotificationMarkReadView,
    PatientListView,
    PatientDetailView,
    MedecinListView,
)
from medisecure.medical.api_views import (
    SpecialiteListView,
    CabinetListView,
    DossierMedicalView,
)
from medisecure.rdv.api_views import (
    PatientRDVListView,
    MedecinPlanningView,
    RDVDetailView,
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("users", UserViewSet)

app_name = "api"
urlpatterns = router.urls + [
    # Tokens JWT
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Auth
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("auth/verify-email/", VerifyEmailView.as_view(), name="verify-email"),
    path(
        "auth/register/patient/",
        PatientRegistrationView.as_view(),
        name="register-patient",
    ),
    path(
        "auth/register/medecin/",
        MedecinRegistrationView.as_view(),
        name="register-medecin",
    ),
    # Profils
    path("patients/", PatientListView.as_view(), name="patients"),
    path(
        "patients/<int:patient_id>/", PatientDetailView.as_view(), name="patient-detail"
    ),
    path("medecins/", MedecinListView.as_view(), name="medecins"),
    # Médical
    path("specialites/", SpecialiteListView.as_view(), name="specialites"),
    path("cabinets/", CabinetListView.as_view(), name="cabinets"),
    path(
        "dossiers/<int:patient_id>/",
        DossierMedicalView.as_view(),
        name="dossier-medical",
    ),
    # Rendez-vous
    path(
        "rdv/patient/<int:patient_id>/",
        PatientRDVListView.as_view(),
        name="rdv-patient",
    ),
    path(
        "rdv/planning/<int:medecin_id>/",
        MedecinPlanningView.as_view(),
        name="rdv-planning",
    ),
    path("rdv/<int:rdv_id>/", RDVDetailView.as_view(), name="rdv-detail"),
    # Notifications
    path("notifications/", NotificationListView.as_view(), name="notifications"),
    path(
        "notifications/<int:notif_id>/read/",
        NotificationMarkReadView.as_view(),
        name="notification-read",
    ),
    # Administration
    path("admin/logs/", LogActiviteListView.as_view(), name="logs"),
    path(
        "admin/users/<int:user_id>/role/",
        UserRoleUpdateView.as_view(),
        name="user-role",
    ),
]
