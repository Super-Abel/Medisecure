from typing import List, Optional
from .entities import RendezVousEntity
from .models import RendezVous


class RendezVousService:
    @staticmethod
    def _to_entity(rdv: RendezVous) -> RendezVousEntity:
        return RendezVousEntity(
            id_rdv=rdv.id,
            patient_id=rdv.patient_id,
            medecin_id=rdv.medecin_id,
            date_heure=rdv.date_heure,
            motif=rdv.motif,
            statut=rdv.statut,
            date_creation=rdv.date_creation,
        )

    def list_by_patient(self, patient_id: int) -> List[RendezVousEntity]:
        return [
            self._to_entity(r) for r in RendezVous.objects.filter(patient_id=patient_id)
        ]

    def list_by_medecin(self, medecin_id: int) -> List[RendezVousEntity]:
        return [
            self._to_entity(r) for r in RendezVous.objects.filter(medecin_id=medecin_id)
        ]

    def reserver(self, entity: RendezVousEntity) -> RendezVousEntity:
        rdv = RendezVous.objects.create(
            patient_id=entity.patient_id,
            medecin_id=entity.medecin_id,
            date_heure=entity.date_heure,
            motif=entity.motif,
        )
        return self._to_entity(rdv)

    def annuler(self, rdv_id: int) -> Optional[RendezVousEntity]:
        try:
            rdv = RendezVous.objects.get(id=rdv_id)
            rdv.statut = "ANNULE"
            rdv.save()
            return self._to_entity(rdv)
        except RendezVous.DoesNotExist:
            return None

    def modifier(
        self, rdv_id: int, date_heure=None, motif=None
    ) -> Optional[RendezVousEntity]:
        try:
            rdv = RendezVous.objects.get(id=rdv_id)
            if date_heure:
                rdv.date_heure = date_heure
            if motif:
                rdv.motif = motif
            rdv.save()
            return self._to_entity(rdv)
        except RendezVous.DoesNotExist:
            return None
