from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import TemplateView, ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from medisecure.users.models import Roles, Medecin, Patient
from medisecure.medical.models import Specialite, DossierMedical
from medisecure.rdv.forms import RendezVousForm
from medisecure.rdv.models import RendezVous, StatutRDV
from django.utils import timezone
from django.contrib.auth.mixins import UserPassesTestMixin


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


class PatientDossierView(LoginRequiredMixin, TemplateView):
    template_name = "portal/patient/dossier.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if hasattr(user, "patient_profile"):
            context["patient"] = user.patient_profile
        return context


class DoctorDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "portal/doctor/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        if hasattr(user, "medecin_profile"):
            medecin = user.medecin_profile
            context["medecin"] = medecin

            # Allow date filtering via query param for testing and future planning
            date_str = self.request.GET.get("date")
            if date_str:
                from datetime import datetime

                try:
                    display_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                except ValueError:
                    display_date = timezone.now().date()
            else:
                display_date = timezone.now().date()

            rdvs_jour = RendezVous.objects.filter(
                medecin=medecin, date_heure__date=display_date
            )
            context["rdv_jour"] = rdvs_jour.order_by("date_heure")
            context["display_date"] = display_date

            # Dynamic stats (for the selected day)
            context["patients_today"] = rdvs_jour.values("patient").distinct().count()

            rdvs_mois = RendezVous.objects.filter(
                medecin=medecin,
                date_heure__month=display_date.month,
                date_heure__year=display_date.year,
            )
            context["rdv_month"] = rdvs_mois.count()
            context["rdv_pending"] = rdvs_mois.filter(
                statut=StatutRDV.EN_ATTENTE
            ).count()
            context["rdv_confirmed"] = rdvs_mois.filter(
                statut=StatutRDV.CONFIRME
            ).count()

        return context


class NurseDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "portal/nurse/dashboard.html"

    def test_func(self):
        return self.request.user.role == Roles.INFIRMIER

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Statistiques factices pour le moment, comme sur le mobile
        context["soins_a_faire"] = 12
        context["urgences"] = 2
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

        qs = Medecin.objects.all()
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


class ConsultationFinishView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        from django.shortcuts import get_object_or_404, redirect

        rdv = get_object_or_404(RendezVous, id=self.kwargs.get("rdv_id"))
        rdv.statut = StatutRDV.TERMINE
        rdv.save()
        messages.success(request, "Consultation terminée avec succès.")
        return redirect("portal:doctor-dashboard")


class DoctorPlanningView(LoginRequiredMixin, TemplateView):
    template_name = "portal/doctor/planning.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from datetime import timedelta

        DAYS_FR = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
        today = timezone.now().date()
        week_start = today - timedelta(days=today.weekday())
        context["week_days"] = [
            {
                "label": DAYS_FR[(week_start + timedelta(days=i)).weekday()],
                "num": (week_start + timedelta(days=i)).day,
                "is_today": (week_start + timedelta(days=i)) == today,
            }
            for i in range(7)
        ]
        if hasattr(self.request.user, "medecin_profile"):
            context["rdvs"] = RendezVous.objects.filter(
                medecin=self.request.user.medecin_profile
            ).order_by("date_heure")
        return context


class DoctorMessagesView(LoginRequiredMixin, TemplateView):
    template_name = "portal/doctor/messages.html"


class DoctorNotificationsView(LoginRequiredMixin, TemplateView):
    template_name = "portal/doctor/notifications.html"


class NursePatientListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = "portal/nurse/patient_list.html"
    context_object_name = "patients"

    def test_func(self):
        return self.request.user.role == Roles.INFIRMIER

    def get_queryset(self):
        # Pour une infirmière, on peut afficher tous les patients ou ceux vus récemment
        # Pour l'instant on affiche tous les patients avec dossier
        return Patient.objects.all().select_related("user")
