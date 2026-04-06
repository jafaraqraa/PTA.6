from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base

class QuizSubmission(Base):
    __tablename__ = "quiz_submissions"

    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="SET NULL"), nullable=True)
    answers = Column(Text, nullable=True) # Store as JSON string of indices
    score = Column(Float, nullable=True) # For grading
    status = Column(String, default="pending") # pending, completed
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    quiz = relationship("Quiz", back_populates="submissions")
    user = relationship("User")
    notes = relationship("InstructorNote", back_populates="submission", cascade="all, delete-orphan")

class InstructorNote(Base):
    __tablename__ = "instructor_notes"

    id = Column(Integer, primary_key=True, index=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submission_id = Column(Integer, ForeignKey("quiz_submissions.id", ondelete="CASCADE"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    author = relationship("User", foreign_keys=[author_id])
    student = relationship("User", foreign_keys=[student_id])
    submission = relationship("QuizSubmission", back_populates="notes")
