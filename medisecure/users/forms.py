from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.core.exceptions import ValidationError
from django.forms import (
    EmailField, CharField, ChoiceField, HiddenInput,
    ModelChoiceField, Form,
)
from django.utils.translation import gettext_lazy as _

from .models import User
from medisecure.medical.models import Specialite, Cabinet


class UserAdminChangeForm(admin_forms.UserChangeForm):
    class Meta(admin_forms.UserChangeForm.Meta):
        model = User
        field_classes = {"email": EmailField}


class UserAdminCreationForm(admin_forms.AdminUserCreationForm):
    """
    Form for User Creation in the Admin Area.
    To change user signup, see UserSignupForm and UserSocialSignupForm.
    """

    class Meta(admin_forms.UserCreationForm.Meta):
        model = User
        fields = ("email",)
        field_classes = {"email": EmailField}
        error_messages = {
            "email": {"unique": _("This email has already been taken.")},
        }


class UserSignupForm(SignupForm):
    nom = CharField(max_length=255, label=_("Nom"), required=True)
    prenom = CharField(max_length=255, label=_("Prénom"), required=True)
    role = ChoiceField(
        choices=[("PATIENT", _("Patient")), ("MEDECIN", _("Médecin"))],
        widget=HiddenInput(),
        initial="PATIENT",
        required=True,
    )

    def __init__(self, *args, **kwargs):
        # Handle initial role from query parameter
        request = kwargs.get("request")
        if request:
            role_param = request.GET.get("role")
            if role_param in ["PATIENT", "MEDECIN"]:
                initial = kwargs.get("initial", {})
                initial["role"] = role_param
                kwargs["initial"] = initial
        super().__init__(*args, **kwargs)

    def save(self, request):
        from .models import Patient, Medecin

        user = super().save(request)
        user.nom = self.cleaned_data["nom"]
        user.prenom = self.cleaned_data["prenom"]
        user.role = self.cleaned_data["role"]
        user.save()

        # Profile creation is handled by signals in medisecure.users.signals

        return user


class MedecinProfilCompletionForm(Form):
    """Collecte les infos professionnelles du médecin après inscription."""

    numero_licence = CharField(
        max_length=100,
        label=_("Numéro de licence médicale"),
        help_text=_("Ex : MED-CM-001234"),
    )
    telephone = CharField(
        max_length=20,
        label=_("Téléphone professionnel"),
        required=False,
        help_text=_("Ex : +237 6XX XXX XXX"),
    )
    specialite = ModelChoiceField(
        queryset=Specialite.objects.all(),
        label=_("Spécialité"),
        empty_label=_("-- Sélectionner une spécialité --"),
    )
    cabinet = ModelChoiceField(
        queryset=Cabinet.objects.all(),
        label=_("Cabinet / Établissement"),
        required=False,
        empty_label=_("-- Sélectionner un établissement (optionnel) --"),
    )

    def clean_numero_licence(self):
        lic = self.cleaned_data["numero_licence"].strip()
        from .models import Medecin
        # Exclure le profil du médecin en cours (passé via initial kwarg)
        qs = Medecin.objects.filter(numero_licence=lic)
        if self._medecin_pk:
            qs = qs.exclude(pk=self._medecin_pk)
        if qs.exists():
            raise ValidationError(_("Ce numéro de licence est déjà utilisé."))
        return lic

    def __init__(self, *args, medecin_pk=None, **kwargs):
        self._medecin_pk = medecin_pk
        super().__init__(*args, **kwargs)


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
