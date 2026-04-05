from pydantic import BaseModel
from datetime import datetime
from app.models.enums import EarSideEnum, TestTypeEnum

class StoredThresholdDTO(BaseModel):
    id: int
    session_id: int
    attempt_id: int
    ear_side: EarSideEnum
    test_type: TestTypeEnum
    frequency: int
    threshold_db: float
    is_no_response: bool
    is_final: bool
    created_at: datetime

    model_config = {"from_attributes": True}

class CreateStoredThresholdDTO(BaseModel):

    session_id: int
    attempt_id: int
    ear_side: EarSideEnum
    test_type: TestTypeEnum
    frequency: int
    threshold_db: float
    is_no_response: bool = False
    is_final: bool = True
