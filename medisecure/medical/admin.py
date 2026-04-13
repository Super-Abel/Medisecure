from django.contrib import admin

from .models import (
    Specialite,
    Cabinet,
    DossierMedical,
    Consultation,
    Prescription,
    ResultatAnalyse,
)


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


@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ["dossier", "medecin", "date_consult", "created_at"]
    search_fields = ["dossier__patient__user__email", "diagnostic"]
    list_filter = ["date_consult"]


@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ["dossier", "medecin", "medicament", "is_active", "created_at"]
    search_fields = ["dossier__patient__user__email", "medicament"]
    list_filter = ["is_active", "created_at"]


@admin.register(ResultatAnalyse)
class ResultatAnalyseAdmin(admin.ModelAdmin):
    list_display = ["dossier", "examen", "statut", "date_examen"]
    search_fields = ["dossier__patient__user__email", "examen"]
    list_filter = ["statut", "date_examen"]
