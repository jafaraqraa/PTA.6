from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class QuizQuestionBase(BaseModel):
    question_text: str
    options: str # JSON string
    correct_option: int

class QuizQuestionCreate(QuizQuestionBase):
    pass

class QuizQuestionDTO(QuizQuestionBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None

class QuizCreate(QuizBase):
    questions: List[QuizQuestionCreate]

class QuizDTO(QuizBase):
    id: int
    created_by_id: int
    university_id: int
    created_at: datetime
    questions: List[QuizQuestionDTO]
    model_config = ConfigDict(from_attributes=True)

class QuizSubmissionCreate(BaseModel):
    quiz_id: int
    answers: str # JSON string of indices

class QuizSubmissionDTO(BaseModel):
    id: int
    quiz_id: int
    user_id: int
    answers: str
    score: Optional[float] = None
    status: str
    created_at: datetime
    notes: List["InstructorNoteDTO"] = []
    model_config = ConfigDict(from_attributes=True)

class InstructorNoteCreate(BaseModel):
    student_id: int
    submission_id: Optional[int] = None
    content: str

class InstructorNoteDTO(InstructorNoteCreate):
    id: int
    author_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
