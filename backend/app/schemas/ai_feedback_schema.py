from typing import List, Optional

from pydantic import BaseModel, Field


class AIFeedbackDTO(BaseModel):
    status: str
    provider: Optional[str] = None
    model: Optional[str] = None
    summary: Optional[str] = None
    strengths: List[str] = Field(default_factory=list)
    improvement_points: List[str] = Field(default_factory=list)
    next_session_tips: List[str] = Field(default_factory=list)
    message: Optional[str] = None

    model_config = {"extra": "forbid"}
