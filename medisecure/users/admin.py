from allauth.account.decorators import secure_admin_login
from django.conf import settings
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.utils.translation import gettext_lazy as _

from .forms import UserAdminChangeForm
from .forms import UserAdminCreationForm
from .models import User, Patient, Medecin, Admin, LogActivite
from .notifications import Notification

if settings.DJANGO_ADMIN_FORCE_ALLAUTH:
    admin.autodiscover()
    admin.site.login = secure_admin_login(admin.site.login)  # type: ignore[method-assign]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Personal info"), {"fields": ("nom", "prenom", "telephone", "role", "statut")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["email", "nom", "prenom", "role", "statut", "is_superuser"]
    search_fields = ["email", "nom", "prenom"]
    list_filter = ["role", "statut", "is_staff"]
    ordering = ["id"]
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "nom", "prenom", "role", "password1", "password2"),
            },
        ),
    )


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ["user", "date_naissance", "sexe"]
    search_fields = ["user__email", "user__nom", "user__prenom"]


@admin.register(Medecin)
class MedecinAdmin(admin.ModelAdmin):
    list_display = ["user", "specialite", "cabinet", "numero_licence"]
    search_fields = ["user__email", "user__nom", "numero_licence"]
    list_filter = ["specialite", "cabinet"]


@admin.register(Admin)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "niveau_acces"]
    search_fields = ["user__email"]


@admin.register(LogActivite)
class LogActiviteAdmin(admin.ModelAdmin):
    list_display = ["date_action", "utilisateur", "action", "adresse_ip"]
    search_fields = ["utilisateur__email", "action"]
    list_filter = ["date_action"]
    readonly_fields = ["utilisateur", "action", "date_action", "adresse_ip"]

    def has_add_permission(self, _request):
        return False

    def has_change_permission(self, _request, _obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ["date_envoi", "utilisateur", "type", "statut"]
    search_fields = ["utilisateur__email", "message"]
    list_filter = ["statut", "type"]
