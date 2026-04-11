from django.contrib import admin

from .models import Specialite, Cabinet, DossierMedical


@admin.register(Specialite)
class SpecialiteAdmin(admin.ModelAdmin):
    list_display = ["nom_specialite", "description"]
    search_fields = ["nom_specialite"]


@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ["nom", "adresse", "telephone"]
    search_fields = ["nom"]


@admin.register(DossierMedical)
class DossierMedicalAdmin(admin.ModelAdmin):
    list_display = ["patient", "date_creation"]
    search_fields = ["patient__user__email"]
    readonly_fields = ["date_creation"]
