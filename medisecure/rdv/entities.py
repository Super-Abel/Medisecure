from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class RendezVousEntity:
    id_rdv: Optional[int]
    patient_id: int
    medecin_id: int
    date_heure: datetime
    motif: str
    statut: str = "EN_ATTENTE"
    date_creation: datetime = field(default_factory=datetime.now)
