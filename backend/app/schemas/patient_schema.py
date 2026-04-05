from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from app.models.enums import (
    EarSideEnum,
    HearingTypeEnum,
    TestTypeEnum,
    PatientSourceEnum,
)

ALLOWED_FREQUENCIES = {125, 250, 500, 750, 1000, 1500, 2000, 3000, 4000, 6000, 8000}


class AudiogramPointDTO(BaseModel):
    id: Optional[int] = None
    test_type: TestTypeEnum
    frequency: int
    threshold_db: float
    is_no_response: bool = False

    @field_validator("frequency")
    @classmethod
    def validate_frequency(cls, value: int) -> int:
        if value not in ALLOWED_FREQUENCIES:
            raise ValueError(f"frequency must be one of {sorted(ALLOWED_FREQUENCIES)}")
        return value

    @field_validator("threshold_db")
    @classmethod
    def validate_threshold_db(cls, value: float) -> float:
        if value < -10 or value > 120:
            raise ValueError("threshold_db must be between -10 and 120")
        return value

    model_config = {"from_attributes": True}


class EarDTO(BaseModel):
    id: Optional[int] = None
    side: EarSideEnum
    hearing_type: Optional[HearingTypeEnum] = None
    hearing_profile: Optional[Dict[int, HearingTypeEnum]] = None
    hearing_tags: List[str] = Field(default_factory=list)
    audiogram_points: List[AudiogramPointDTO] = Field(default_factory=list)

    @field_validator("hearing_profile")
    @classmethod
    def validate_hearing_profile(cls, value: Optional[Dict[int, HearingTypeEnum]]) -> Optional[Dict[int, HearingTypeEnum]]:
        if value is None:
            return value
        cleaned: Dict[int, HearingTypeEnum] = {}
        for k, v in value.items():
            try:
                freq = int(k)
            except (TypeError, ValueError):
                raise ValueError("hearing_profile keys must be frequencies")
            if freq not in ALLOWED_FREQUENCIES:
                raise ValueError(f"hearing_profile frequency must be one of {sorted(ALLOWED_FREQUENCIES)}")
            cleaned[freq] = HearingTypeEnum(v)
        return cleaned

    model_config = {"from_attributes": True}


class PatientDTO(BaseModel):
    id: Optional[int] = None
    source_type: PatientSourceEnum = PatientSourceEnum.REAL
    image_ref: Optional[str] = None
    ears: List[EarDTO] = Field(default_factory=list)

    model_config = {"from_attributes": True}
    
