from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.enums import EarSideEnum, TestTypeEnum

class StoredThreshold(Base):
    __tablename__ = "stored_thresholds"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    attempt_id = Column(Integer, ForeignKey("attempts.id", ondelete="CASCADE"), nullable=False)

    ear_side = Column(SQLEnum(EarSideEnum), nullable=False)
    test_type = Column(SQLEnum(TestTypeEnum), nullable=False)

    frequency = Column(Integer, nullable=False)
    threshold_db = Column(Float, nullable=False)
    is_no_response = Column(Boolean, nullable=False, default=False)
    is_final = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    session = relationship("Session", back_populates="stored_thresholds")
    attempt = relationship("Attempt")
