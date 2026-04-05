from pydantic import BaseModel, Field, field_validator, model_validator
from typing import List, Optional

from app.models.enums import (
    EarSideEnum,
    HearingTypeEnum,
    HearingSeverityEnum,
    HearingConfigurationEnum,
)
from app.schemas.patient_schema import ALLOWED_FREQUENCIES


class FinalInterpretationCreateDTO(BaseModel):
    ear_side: EarSideEnum
    overall_type: Optional[HearingTypeEnum] = None
    severity: Optional[HearingSeverityEnum] = None
    configuration: Optional[HearingConfigurationEnum] = None
    affected_frequencies_hz: List[int] = Field(default_factory=list)

    @field_validator("affected_frequencies_hz")
    @classmethod
    def validate_affected_frequencies(cls, value: List[int]) -> List[int]:
        cleaned: List[int] = []
        seen: set[int] = set()
        for freq in value:
            if freq not in ALLOWED_FREQUENCIES:
                raise ValueError(f"affected_frequencies_hz must be within {sorted(ALLOWED_FREQUENCIES)}")
            if freq not in seen:
                seen.add(freq)
                cleaned.append(freq)
        return cleaned

    @model_validator(mode="after")
    def validate_diagnosis_consistency(self) -> "FinalInterpretationCreateDTO":
        if self.overall_type == HearingTypeEnum.NORMAL and self.severity not in {
            None,
            HearingSeverityEnum.NORMAL,
        }:
            raise ValueError("Normal hearing type can only be paired with Normal severity")

        if self.severity == HearingSeverityEnum.NORMAL and self.overall_type not in {
            None,
            HearingTypeEnum.NORMAL,
        }:
            raise ValueError("Normal severity can only be paired with Normal hearing type")

        if (
            self.overall_type is not None
            and self.overall_type != HearingTypeEnum.NORMAL
            and self.severity is None
        ):
            raise ValueError("severity is required when a hearing-loss type is selected")

        if self.overall_type == HearingTypeEnum.NORMAL and self.affected_frequencies_hz:
            raise ValueError("Normal hearing interpretation should not include affected frequencies")

        if self.configuration == HearingConfigurationEnum.SINGLE_FREQUENCY and len(self.affected_frequencies_hz) != 1:
            raise ValueError("Single Frequency configuration requires exactly one affected frequency")

        if (
            self.configuration in {
                HearingConfigurationEnum.ALL_FREQUENCIES,
                HearingConfigurationEnum.LOW_FREQUENCIES,
                HearingConfigurationEnum.MID_FREQUENCIES,
                HearingConfigurationEnum.HIGH_FREQUENCIES,
                HearingConfigurationEnum.NOTCH_PATTERN,
            }
            and not self.affected_frequencies_hz
            and self.overall_type not in {None, HearingTypeEnum.NORMAL}
        ):
            raise ValueError("affected_frequencies_hz is required for hearing-loss configuration selection")

        return self


class FinalInterpretationDTO(FinalInterpretationCreateDTO):
    id: int
    session_id: int
    clinical_comment: Optional[str] = None

    model_config = {"from_attributes": True}


class EndSessionDTO(BaseModel):
    session_id: int
    interpretations: List[FinalInterpretationCreateDTO] = Field(min_length=1)

    @field_validator("interpretations")
    @classmethod
    def validate_unique_ears(cls, value: List[FinalInterpretationCreateDTO]) -> List[FinalInterpretationCreateDTO]:
        ears = [item.ear_side for item in value]
        if len(set(ears)) != len(ears):
            raise ValueError("Each ear can only be interpreted once per submission")
        return value
