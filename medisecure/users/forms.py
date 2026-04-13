from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django.contrib.auth import forms as admin_forms
from django.forms import EmailField, CharField, ChoiceField, HiddenInput
from django.utils.translation import gettext_lazy as _

from .models import User


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


class UserSocialSignupForm(SocialSignupForm):
    """
    Renders the form when user has signed up using social accounts.
    Default fields will be added automatically.
    See UserSignupForm otherwise.
    """
