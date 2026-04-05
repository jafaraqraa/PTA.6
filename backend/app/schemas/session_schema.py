from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.schemas.patient_schema import PatientDTO
from app.schemas.attempt_schema import AttemptDTO
from app.schemas.stored_threshold_schema import StoredThresholdDTO
from app.schemas.final_interpretation_schema import FinalInterpretationDTO


class SessionCreateDTO(BaseModel):
    user_id: int
    patient_id: Optional[int] = None
    
    model_config = {"from_attributes": True}


class SessionDTO(BaseModel):
    id: int
    user_id: int
    patient_id: Optional[int] = None
    start_time: datetime
    end_time: Optional[datetime] = None

    model_config = {"from_attributes": True}


class SessionFullDTO(SessionDTO):
    patient: Optional[PatientDTO] = None
    attempts: List[AttemptDTO] = Field(default_factory=list)
    stored_thresholds: List[StoredThresholdDTO] = Field(default_factory=list)
    final_interpretations: List[FinalInterpretationDTO] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SessionWithPatientDTO(SessionDTO):
    patient: Optional[PatientDTO] = None

    model_config = {"from_attributes": True}
