from typing import List
from medisecure.domain.models import SpecialiteEntity, CabinetEntity
from medisecure.domain.repositories import SpecialiteRepository, CabinetRepository


class MedicalService:
    def __init__(
        self, specialite_repo: SpecialiteRepository, cabinet_repo: CabinetRepository
    ):
        self.specialite_repo = specialite_repo
        self.cabinet_repo = cabinet_repo

    def list_specialites(self) -> List[SpecialiteEntity]:
        return self.specialite_repo.get_all()

    def list_cabinets(self) -> List[CabinetEntity]:
        return self.cabinet_repo.get_all()
