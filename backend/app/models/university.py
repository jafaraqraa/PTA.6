from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class University(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="university")
    subscriptions = relationship("Subscription", back_populates="university")
