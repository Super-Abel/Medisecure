from django.urls import path
from medisecure.medical.api_views import DossierPDFView
from .views import (
    PatientDashboardView,
    PatientDossierView,
    DoctorDashboardView,
    BookingView,
    DoctorSearchView,
    BookingConfirmView,
    DoctorPatientListView,
    DoctorDossierUpdateView,
    ConsultationFinishView,
    DoctorPlanningView,
    DoctorMessagesView,
    DoctorNotificationsView,
    NurseDashboardView,
    NursePatientListView,
)

app_name = "portal"
urlpatterns = [
    path("patient/", PatientDashboardView.as_view(), name="patient-dashboard"),
    path("patient/dossier/", PatientDossierView.as_view(), name="patient-dossier"),
    path("patient/booking/", BookingView.as_view(), name="patient-booking"),
    path("patient/booking/search/", DoctorSearchView.as_view(), name="doctor-search"),
    path(
        "patient/booking/<int:medecin_id>/",
        BookingConfirmView.as_view(),
        name="booking-confirm",
    ),
    path("doctor/", DoctorDashboardView.as_view(), name="doctor-dashboard"),
    path("doctor/patients/", DoctorPatientListView.as_view(), name="doctor-patients"),
    path("doctor/planning/", DoctorPlanningView.as_view(), name="doctor-planning"),
    path("doctor/messages/", DoctorMessagesView.as_view(), name="doctor-messages"),
    path(
        "doctor/notifications/",
        DoctorNotificationsView.as_view(),
        name="doctor-notifications",
    ),
    path(
        "doctor/patients/<int:patient_id>/dossier/",
        DoctorDossierUpdateView.as_view(),
        name="doctor-dossier",
    ),
    path(
        "doctor/rdv/<int:rdv_id>/finish/",
        ConsultationFinishView.as_view(),
        name="rdv-finish",
    ),
    path("nurse/", NurseDashboardView.as_view(), name="nurse-dashboard"),
    path("nurse/patients/", NursePatientListView.as_view(), name="nurse-patients"),
    path(
        "patients/<int:patient_id>/dossier/pdf/",
        DossierPDFView.as_view(),
        name="dossier-pdf",
    ),
    path(
        "patients/dossier/pdf/",
        DossierPDFView.as_view(),
        name="dossier-pdf-self",
    ),
]
