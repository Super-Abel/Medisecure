from typing import Optional
from medisecure.domain.models import DossierMedicalEntity
from medisecure.domain.repositories import DossierMedicalRepository


class DossierMedicalService:
    def __init__(self, dossier_repo: DossierMedicalRepository):
        self.dossier_repo = dossier_repo

    def get_patient_dossier(self, patient_id: int) -> Optional[DossierMedicalEntity]:
        # Logique de contrôle d'accès pourra être ajoutée ici
        return self.dossier_repo.get_by_patient_id(patient_id)

    def save_dossier(self, dossier: DossierMedicalEntity) -> DossierMedicalEntity:
        return self.dossier_repo.save(dossier)
