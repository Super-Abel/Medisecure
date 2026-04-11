from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from medisecure.users.models import Roles, Medecin, Patient
from medisecure.medical.models import Specialite, DossierMedical
from medisecure.rdv.forms import RendezVousForm
from medisecure.rdv.models import RendezVous, StatutRDV
from django.utils import timezone


class PatientDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "portal/patient/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # S'assurer que c'est un patient
        if hasattr(user, "patient_profile"):
            patient = user.patient_profile
            context["patient"] = patient
            context["rdv_recents"] = RendezVous.objects.filter(
                patient=patient
            ).order_by("-date_heure")[:5]
            context["dossier"] = DossierMedical.objects.filter(patient=patient).first()

        return context


class DoctorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "portal/doctor/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if hasattr(user, "medecin_profile"):
            medecin = user.medecin_profile
            context["medecin"] = medecin
            aujourd_hui = timezone.now().date()
            context["rdv_jour"] = RendezVous.objects.filter(
                medecin=medecin, date_heure__date=aujourd_hui
            ).order_by("date_heure")

        return context


class BookingView(LoginRequiredMixin, TemplateView):
    template_name = "portal/patient/booking.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["specialites"] = Specialite.objects.all()
        return context


class DoctorSearchView(LoginRequiredMixin, ListView):
    template_name = "portal/patient/partials/doctor_results.html"
    context_object_name = "medecins"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        spec_id = self.request.GET.get("specialite", "")

        qs = Medecin.objects.select_related("user", "specialite", "cabinet")
        if spec_id:
            qs = qs.filter(specialite_id=spec_id)
        if query:
            qs = qs.filter(user__nom__icontains=query)
        return qs


class BookingConfirmView(LoginRequiredMixin, CreateView):
    model = RendezVous
    form_class = RendezVousForm
    template_name = "portal/patient/booking_confirm.html"
    success_url = reverse_lazy("portal:patient-dashboard")

    def form_valid(self, form):
        form.instance.patient = self.request.user.patient_profile
        form.instance.medecin_id = self.kwargs.get("medecin_id")
        form.instance.statut = StatutRDV.EN_ATTENTE
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["medecin"] = Medecin.objects.get(id=self.kwargs.get("medecin_id"))
        return context


class DoctorPatientListView(LoginRequiredMixin, ListView):
    template_name = "portal/doctor/patient_list.html"
    context_object_name = "patients"

    def get_queryset(self):
        medecin = self.request.user.medecin_profile
        # Récupère les patients uniques liés aux RDV de ce médecin
        patient_ids = (
            RendezVous.objects.filter(medecin=medecin)
            .values_list("patient_id", flat=True)
            .distinct()
        )
        return Patient.objects.filter(id__in=patient_ids).select_related("user")


class DoctorDossierUpdateView(LoginRequiredMixin, UpdateView):
    model = DossierMedical
    template_name = "portal/doctor/dossier_form.html"
    fields = ["antecedents", "allergies"]
    success_url = reverse_lazy("portal:doctor-patients")

    def get_object(self, queryset=None):
        patient_id = self.kwargs.get("patient_id")
        obj, created = DossierMedical.objects.get_or_create(patient_id=patient_id)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["patient"] = Patient.objects.get(id=self.kwargs.get("patient_id"))
        return context


class ConsultationFinishView(LoginRequiredMixin, UpdateView):
    model = RendezVous
    fields = []
    success_url = reverse_lazy("portal:doctor-dashboard")

    def post(self, request, *args, **kwargs):
        rdv = self.get_object()
        rdv.statut = StatutRDV.TERMINE
        rdv.save()
        return super().post(request, *args, **kwargs)

    def get_object(self, queryset=None):
        return RendezVous.objects.get(id=self.kwargs.get("rdv_id"))
