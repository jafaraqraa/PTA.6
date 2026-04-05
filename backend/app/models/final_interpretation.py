from sqlalchemy import Column, Integer, ForeignKey, Enum as SQLEnum, Text, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.enums import (
    EarSideEnum,
    HearingTypeEnum,
    HearingSeverityEnum,
    HearingConfigurationEnum,
)


class FinalInterpretation(Base):
    __tablename__ = "final_interpretations"
    __table_args__ = (
        UniqueConstraint("session_id", "ear_side", name="uq_final_interpretation_session_ear"),
    )

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
    )

    ear_side = Column(SQLEnum(EarSideEnum), nullable=False)
    overall_type = Column(SQLEnum(HearingTypeEnum), nullable=True)
    severity = Column(SQLEnum(HearingSeverityEnum), nullable=True)
    configuration = Column(SQLEnum(HearingConfigurationEnum, name="hearingdistributionenum"), nullable=True)
    affected_frequencies_hz = Column(JSON, nullable=False, default=list)
    clinical_comment = Column(Text, nullable=True)

    session = relationship("Session", back_populates="final_interpretations")
