from __future__ import annotations

from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import RendezVous


class RendezVousForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ["date_heure", "motif"]

    def clean_date_heure(self):
        date_heure = self.cleaned_data.get("date_heure")
        if date_heure and date_heure <= timezone.now():
            raise forms.ValidationError(_("La date du rendez-vous doit être dans le futur."))
        return date_heure
