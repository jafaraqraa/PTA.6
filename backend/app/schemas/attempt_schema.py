from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.enums import EarSideEnum, TestTypeEnum, ResponseEnum

class AttemptCreateDTO(BaseModel):
    session_id: int
    ear_side: EarSideEnum
    test_type: TestTypeEnum
    frequency: int
    intensity: float
    masking_level_db: Optional[float] = None
    response: Optional[ResponseEnum] = None

class AttemptDTO(AttemptCreateDTO):
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}
