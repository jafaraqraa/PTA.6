from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base
from app.models.enums import EarSideEnum, ResponseEnum, TestTypeEnum

class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)

    # TONE
    ear_side = Column(SQLEnum(EarSideEnum), nullable=False)      # left / right
    test_type = Column(SQLEnum(TestTypeEnum), nullable=False)     # AC / AC_masked / BC / BC_masked
    frequency = Column(Integer, nullable=False)        # 250, 500, 1000...
    intensity = Column(Float, nullable=False)          # dB level
    masking_level_db = Column(Float, nullable=True)    # masking noise level (if used)
    response = Column(SQLEnum(ResponseEnum), nullable=True)       # heard / not_heard 

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
    session = relationship("Session", back_populates="attempts")
