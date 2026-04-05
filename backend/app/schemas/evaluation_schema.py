from typing import Any, List, Optional

from pydantic import BaseModel, Field

from app.models.enums import EarSideEnum, TestTypeEnum
from app.schemas.ai_feedback_schema import AIFeedbackDTO


class ProtocolMetricDTO(BaseModel):
    code: str
    label: str
    score: float
    max_score: float = 100.0
    status: str
    details: str


class ThresholdComparisonDTO(BaseModel):
    ear_side: EarSideEnum
    test_type: TestTypeEnum
    frequency: int
    true_threshold_db: Optional[float] = None
    detected_threshold_db: Optional[float] = None
    true_is_no_response: bool = False
    detected_is_no_response: bool = False
    absolute_error_db: Optional[float] = None
    score: float
    status: str
    note: str


class InterpretationFieldScoreDTO(BaseModel):
    field_name: str
    expected_value: Any = None
    submitted_value: Any = None
    score: float
    max_score: float = 100.0
    is_scorable: bool = True
    status: str = "scored"
    note: str


class EarInterpretationEvaluationDTO(BaseModel):
    ear_side: EarSideEnum
    score: float
    max_score: float = 100.0
    scorable_fields: List[str] = Field(default_factory=list)
    undetermined_fields: dict[str, str] = Field(default_factory=dict)
    reference_summary: dict[str, Any] = Field(default_factory=dict)
    submitted_summary: Optional[dict[str, Any]] = None
    field_scores: List[InterpretationFieldScoreDTO] = Field(default_factory=list)


class EvaluationSummaryDTO(BaseModel):
    session_id: int
    patient_id: Optional[int] = None
    duration_seconds: Optional[float] = None
    overall_score: float
    threshold_accuracy_score: float
    interpretation_score: float
    protocol_feedback_summary: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    improvement_points: List[str] = Field(default_factory=list)


class SessionEvaluationDTO(BaseModel):
    summary: EvaluationSummaryDTO
    protocol_metrics: List[ProtocolMetricDTO] = Field(default_factory=list)
    threshold_comparisons: List[ThresholdComparisonDTO] = Field(default_factory=list)
    interpretation_evaluations: List[EarInterpretationEvaluationDTO] = Field(default_factory=list)
    ai_feedback: Optional[AIFeedbackDTO] = None
