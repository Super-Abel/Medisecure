from typing import List, Optional
from medisecure.domain.models import (
    SpecialiteEntity,
    CabinetEntity,
    DossierMedicalEntity,
)
from medisecure.domain.repositories import (
    SpecialiteRepository,
    CabinetRepository,
    DossierMedicalRepository,
)
from .models import Specialite, Cabinet, DossierMedical
from .encryption import AESService


class DjangoSpecialiteRepository(SpecialiteRepository):
    def get_all(self) -> List[SpecialiteEntity]:
        return [
            SpecialiteEntity(
                id_specialite=s.id,
                nom_specialite=s.nom_specialite,
                description=s.description,
            )
            for s in Specialite.objects.all()
        ]


class DjangoCabinetRepository(CabinetRepository):
    def get_all(self) -> List[CabinetEntity]:
        return [
            CabinetEntity(
                id_cabinet=c.id, nom=c.nom, adresse=c.adresse, telephone=c.telephone
            )
            for c in Cabinet.objects.all()
        ]


class DjangoDossierMedicalRepository(DossierMedicalRepository):
    def get_by_patient_id(self, patient_id: int) -> Optional[DossierMedicalEntity]:
        try:
            d = DossierMedical.objects.get(patient_id=patient_id)
            return DossierMedicalEntity(
                id_dossier=d.id,
                patient_id=d.patient_id,
                antecedents=AESService.decrypt(d.antecedents),
                allergies=AESService.decrypt(d.allergies),
                traitements=AESService.decrypt(d.traitements),
                date_creation=d.date_creation,
            )
        except DossierMedical.DoesNotExist:
            return None

    def save(self, dossier: DossierMedicalEntity) -> DossierMedicalEntity:
        d, created = DossierMedical.objects.update_or_create(
            patient_id=dossier.patient_id,
            defaults={
                "antecedents": AESService.encrypt(dossier.antecedents),
                "allergies": AESService.encrypt(dossier.allergies),
                "traitements": AESService.encrypt(dossier.traitements),
            },
        )
        dossier.id_dossier = d.id
        return dossier
