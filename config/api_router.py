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
    NurseRegistrationView,
    VerifyEmailView,
    CustomTokenRefreshView,
    PatientMeProfileView,
    NurseCreatePatientView,
)
from medisecure.users.admin_views import LogActiviteListView, UserRoleUpdateView
from medisecure.users.profile_views import (
    NotificationListView,
    NotificationMarkReadView,
    NotificationReadAllView,
    NotificationUnreadCountView,
    PatientListView,
    PatientDetailView,
    MedecinListView,
    PlanningRdvByDateView,
    AvailableSlotsView,
    UpdateAvailabilityView,
)
from medisecure.medical.api_views import (
    SpecialiteListView,
    CabinetListView,
    DossierMedicalView,
    DossierPDFView,
    PrescriptionViewSet,
    ConsultationViewSet,
    ResultatAnalyseViewSet,
    SignesVitauxViewSet,
)
from medisecure.rdv.api_views import (
    PatientRDVListView,
    MedecinPlanningView,
    RDVDetailView,
)

router = DefaultRouter() if settings.DEBUG else SimpleRouter()
router.register("users", UserViewSet)
router.register("prescriptions", PrescriptionViewSet, basename="prescription")
router.register("consultations", ConsultationViewSet, basename="consultation")
router.register("resultats-labo", ResultatAnalyseViewSet, basename="resultat-analyse")
router.register("vitals", SignesVitauxViewSet, basename="signes-vitaux")

app_name = "api"
urlpatterns = (
    [
        # --- Alias pour l'App Mobile (Prioritaires) ---
        # Auth
        path(
            "auth/refresh/",
            CustomTokenRefreshView.as_view(),
            name="mobile-auth-refresh",
        ),
        # Appointments
        path(
            "appointments/",
            PatientRDVListView.as_view(),
            name="mobile-appointments-list",
        ),
        path(
            "users/specialties/",
            SpecialiteListView.as_view(),
            name="mobile-users-specialties",
        ),
        path("users/doctors/", MedecinListView.as_view(), name="mobile-users-doctors"),
        path(
            "users/patient/profile/",
            PatientMeProfileView.as_view(),
            name="mobile-patient-profile",
        ),
        path(
            "appointments/<int:rdv_id>/",
            RDVDetailView.as_view(),
            name="mobile-appointment-detail",
        ),
        path(
            "appointments/slots/<int:medecin_id>/",
            AvailableSlotsView.as_view(),
            name="mobile-appointment-slots",
        ),
        # Records
        path("records/my/", DossierMedicalView.as_view(), name="mobile-record-my"),
        path(
            "records/<int:patient_id>/",
            DossierMedicalView.as_view(),
            name="mobile-record-detail",
        ),
        path(
            "records/<int:patient_id>/prescriptions",
            PrescriptionViewSet.as_view({"post": "create"}),
            name="mobile-record-prescriptions",
        ),
        path(
            "records/<int:patient_id>/consultations",
            ConsultationViewSet.as_view({"post": "create"}),
            name="mobile-record-consultations",
        ),
        path(
            "records/<int:patient_id>/lab-results",
            ResultatAnalyseViewSet.as_view({"post": "create"}),
            name="mobile-record-lab-results",
        ),
        path(
            "records/<int:patient_id>/prescriptions/<int:pk>",
            PrescriptionViewSet.as_view({"delete": "destroy"}),
            name="mobile-record-prescription-detail",
        ),
        path(
            "records/<int:patient_id>/vitals",
            SignesVitauxViewSet.as_view({"post": "create"}),
            name="mobile-record-vitals",
        ),
        path(
            "records/<int:patient_id>/pdf/",
            DossierPDFView.as_view(),
            name="mobile-record-pdf",
        ),
        path(
            "records/my/pdf/",
            DossierPDFView.as_view(),
            name="mobile-record-pdf-self",
        ),
    ]
    + router.urls
    + [
        # Tokens JWT
        path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
        path(
            "auth/token/refresh/",
            CustomTokenRefreshView.as_view(),
            name="token_refresh",
        ),
        # Auth
        path("auth/login/", LoginView.as_view(), name="login"),
        path("auth/logout/", LogoutView.as_view(), name="logout"),
        path(
            "auth/forgot-password/",
            ForgotPasswordView.as_view(),
            name="forgot-password",
        ),
        path(
            "auth/reset-password/", ResetPasswordView.as_view(), name="reset-password"
        ),
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
        path(
            "auth/register/infirmier/",
            NurseRegistrationView.as_view(),
            name="register-infirmier",
        ),
        path(
            "auth/nurse-create-patient/",
            NurseCreatePatientView.as_view(),
            name="nurse-create-patient",
        ),
        # Profils
        path("patients/", PatientListView.as_view(), name="patients"),
        path(
            "patients/<int:patient_id>/",
            PatientDetailView.as_view(),
            name="patient-detail",
        ),
        path("medecins/", MedecinListView.as_view(), name="medecins"),
        path(
            "medecins/<int:medecin_id>/slots/",
            AvailableSlotsView.as_view(),
            name="medecin-slots",
        ),
        path(
            "medecins/me/disponibilites/",
            UpdateAvailabilityView.as_view(),
            name="medecin-disponibilites-update",
        ),
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
        path("notifications/", NotificationListView.as_view(), name="notifications"),
        path(
            "notifications/<int:notif_id>/read/",
            NotificationMarkReadView.as_view(),
            name="notification-read",
        ),
        path(
            "notifications/read-all/",
            NotificationReadAllView.as_view(),
            name="notifications-read-all",
        ),
        path(
            "notifications/unread-count/",
            NotificationUnreadCountView.as_view(),
            name="notifications-unread-count",
        ),
        # Administration
        path("admin/logs/", LogActiviteListView.as_view(), name="logs"),
        path(
            "admin/users/<int:user_id>/role/",
            UserRoleUpdateView.as_view(),
            name="user-role",
        ),
        path("planning/rdvs/", PlanningRdvByDateView.as_view(), name="planning-rdvs"),
    ]
)
