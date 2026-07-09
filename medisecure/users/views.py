from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, FormView, RedirectView, UpdateView

from medisecure.users.models import User, Roles
from medisecure.users.forms import MedecinProfilCompletionForm

if TYPE_CHECKING:
    from django.db.models import QuerySet


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    slug_field = "id"
    slug_url_kwarg = "id"


user_detail_view = UserDetailView.as_view()


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    fields = ["name"]
    success_message = _("Information successfully updated")

    def get_success_url(self) -> str:
        assert self.request.user.is_authenticated
        return self.request.user.get_absolute_url()

    def get_object(self, queryset: QuerySet | None = None) -> User:
        assert self.request.user.is_authenticated
        return self.request.user


user_update_view = UserUpdateView.as_view()


def _medecin_profile_incomplete(user) -> bool:
    """True si le médecin n'a pas encore complété son profil professionnel."""
    try:
        m = user.medecin_profile
        return not m.specialite_id or m.numero_licence.startswith("LIC-")
    except Exception:
        return True


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs) -> str:
        user = self.request.user
        if user.role == Roles.MEDECIN and _medecin_profile_incomplete(user):
            return reverse("users:complete-medecin-profil")
        if user.role == Roles.PATIENT:
            return reverse("portal:patient-dashboard")
        elif user.role == Roles.MEDECIN:
            return reverse("portal:doctor-dashboard")
        elif user.is_staff or user.role == Roles.ADMIN:
            return reverse("admin_panel:dashboard")
        return reverse("users:detail", kwargs={"pk": user.pk})


user_redirect_view = UserRedirectView.as_view()


class MedecinProfilCompletionView(LoginRequiredMixin, FormView):
    """Étape 2 : le médecin complète spécialité, licence et cabinet."""

    template_name = "users/medecin_profil_completion.html"
    form_class = MedecinProfilCompletionForm

    def dispatch(self, request, *args, **kwargs):
        # Seuls les médecins avec un profil incomplet accèdent à cette page
        if request.user.is_authenticated:
            if request.user.role != Roles.MEDECIN:
                return self._redirect_dashboard()
            if not _medecin_profile_incomplete(request.user):
                return self._redirect_dashboard()
        return super().dispatch(request, *args, **kwargs)

    def _redirect_dashboard(self):
        from django.shortcuts import redirect
        return redirect(reverse("portal:doctor-dashboard"))

    def get_form_kwargs(self):
        kw = super().get_form_kwargs()
        try:
            kw["medecin_pk"] = self.request.user.medecin_profile.pk
        except Exception:
            kw["medecin_pk"] = None
        return kw

    def form_valid(self, form):
        user = self.request.user
        medecin = user.medecin_profile

        medecin.numero_licence = form.cleaned_data["numero_licence"]
        medecin.specialite = form.cleaned_data["specialite"]
        medecin.cabinet = form.cleaned_data.get("cabinet")
        medecin.save()

        if form.cleaned_data.get("telephone"):
            user.telephone = form.cleaned_data["telephone"]
            user.save(update_fields=["telephone"])

        messages.success(
            self.request,
            "Votre profil professionnel a été complété. Bienvenue sur MediSecure !"
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("portal:doctor-dashboard")


medecin_profil_completion_view = MedecinProfilCompletionView.as_view()
