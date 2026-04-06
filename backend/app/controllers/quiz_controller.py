from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.security_utils import get_current_user, check_role
from app.services.quiz_service import QuizService, NoteService
from app.schemas.quiz_schema import (
    QuizCreate, QuizDTO, QuizSubmissionCreate, QuizSubmissionDTO,
    InstructorNoteCreate, InstructorNoteDTO
)
from app.models.enums import UserRoleEnum
from typing import List

router = APIRouter()

@router.post("/")
async def create_quiz(
    data: QuizCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_role([UserRoleEnum.UNIVERSITY_ADMIN, UserRoleEnum.LAB_ADMIN]))
):
    return await QuizService.create_quiz(db, current_user.university_id, current_user.id, data.model_dump())

@router.get("/")
async def list_quizzes(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await QuizService.list_quizzes(db, current_user.university_id)

@router.post("/submit")
async def submit_quiz(
    data: QuizSubmissionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_role([UserRoleEnum.STUDENT]))
):
    return await QuizService.submit_quiz(db, current_user.id, data.quiz_id, data.answers)

@router.get("/submissions/{quiz_id}", response_model=List[QuizSubmissionDTO])
async def list_quiz_submissions(
    quiz_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_role([UserRoleEnum.UNIVERSITY_ADMIN, UserRoleEnum.LAB_ADMIN]))
):
    return await QuizService.list_submissions_for_quiz(db, quiz_id)

@router.get("/my-submissions")
async def my_submissions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return await QuizService.list_submissions_for_user(db, current_user.id)

@router.post("/notes")
async def add_note(
    data: InstructorNoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_role([UserRoleEnum.UNIVERSITY_ADMIN, UserRoleEnum.LAB_ADMIN]))
):
    return await NoteService.create_note(db, current_user.id, data.model_dump())

@router.get("/notes/{student_id}")
async def get_notes(
    student_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Security check: if not super admin, must be same university
    if current_user.role != UserRoleEnum.SUPER_ADMIN:
         # Need to verify student belongs to university
         from app.services.user_service import UserService
         student = await UserService.get_user_by_id(db, student_id)
         if not student or student.university_id != current_user.university_id:
              raise HTTPException(status_code=403, detail="Not authorized")

    return await NoteService.list_notes_for_student(db, student_id)
