from abc import ABC, abstractmethod
from typing import Optional, List
from .models import (
    UserEntity,
    LogEntity,
    SpecialiteEntity,
    CabinetEntity,
    DossierMedicalEntity,
)


class UserRepository(ABC):
    @abstractmethod
    def get_by_email(self, email: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def save(self, user: UserEntity) -> UserEntity:
        pass


class SpecialiteRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[SpecialiteEntity]:
        pass


class CabinetRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[CabinetEntity]:
        pass


class DossierMedicalRepository(ABC):
    @abstractmethod
    def get_by_patient_id(self, patient_id: int) -> Optional[DossierMedicalEntity]:
        pass

    @abstractmethod
    def save(self, dossier: DossierMedicalEntity) -> DossierMedicalEntity:
        pass


class LogRepository(ABC):
    @abstractmethod
    def record(self, log: LogEntity) -> None:
        pass
