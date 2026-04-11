from django.urls import path
from .views import (
    PatientDashboardView,
    DoctorDashboardView,
    BookingView,
    DoctorSearchView,
    BookingConfirmView,
    DoctorPatientListView,
    DoctorDossierUpdateView,
    ConsultationFinishView,
)

app_name = "portal"
urlpatterns = [
    path("patient/", PatientDashboardView.as_view(), name="patient-dashboard"),
    path("patient/booking/", BookingView.as_view(), name="patient-booking"),
    path("patient/booking/search/", DoctorSearchView.as_view(), name="doctor-search"),
    path(
        "patient/booking/<int:medecin_id>/",
        BookingConfirmView.as_view(),
        name="booking-confirm",
    ),
    path("doctor/", DoctorDashboardView.as_view(), name="doctor-dashboard"),
    path("doctor/patients/", DoctorPatientListView.as_view(), name="doctor-patients"),
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
]
