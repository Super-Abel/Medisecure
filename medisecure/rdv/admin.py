from django.contrib import admin

from .models import RendezVous


@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ["patient", "medecin", "date_heure", "statut", "motif"]
    search_fields = ["patient__user__email", "medecin__user__email", "motif"]
    list_filter = ["statut", "date_heure"]
    readonly_fields = ["date_creation"]
