from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


class UserRole(Enum):
    PATIENT = "PATIENT"
    MEDECIN = "MEDECIN"
    INFIRMIER = "INFIRMIER"
    ADMIN = "ADMIN"


@dataclass
class UserEntity:
    id_utilisateur: Optional[int]
    nom: str
    prenom: str
    email: str
    role: UserRole
    telephone: Optional[str] = None
    statut: bool = True
    date_creation: datetime = field(default_factory=datetime.now)


@dataclass
class PatientEntity:
    id_patient: Optional[int]
    utilisateur: UserEntity
    date_naissance: Optional[datetime] = None
    sexe: Optional[str] = None
    adresse: Optional[str] = None


@dataclass
class SpecialiteEntity:
    id_specialite: Optional[int]
    nom_specialite: str
    description: Optional[str] = None


@dataclass
class CabinetEntity:
    id_cabinet: Optional[int]
    nom: str
    adresse: Optional[str] = None
    telephone: Optional[str] = None


@dataclass
class MedecinEntity:
    id_medecin: Optional[int]
    utilisateur: UserEntity
    specialite: SpecialiteEntity
    numero_licence: str
    cabinet: Optional[CabinetEntity] = None


@dataclass
class AdminEntity:
    id_admin: Optional[int]
    utilisateur: UserEntity
    niveau_acces: Optional[str] = None


@dataclass
class DossierMedicalEntity:
    id_dossier: Optional[int]
    patient_id: int
    antecedents: str  # Sera chiffré
    allergies: str  # Sera chiffré
    traitements: str  # Sera chiffré
    date_creation: datetime = field(default_factory=datetime.now)


@dataclass
class LogEntity:
    id_log: Optional[int]
    utilisateur_id: int
    action: str
    adresse_ip: Optional[str] = None
    date_action: datetime = field(default_factory=datetime.now)
