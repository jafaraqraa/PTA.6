from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from app.models.quiz import Quiz, QuizQuestion
from app.models.quiz_submission import QuizSubmission, InstructorNote
from app.schemas.quiz_schema import QuizDTO, QuizQuestionDTO, QuizSubmissionDTO, InstructorNoteDTO
from typing import List, Optional
import json

class QuizService:
    @staticmethod
    async def create_quiz(db: AsyncSession, university_id: int, creator_id: int, data: dict) -> dict:
        questions_data = data.pop("questions", [])
        new_quiz = Quiz(
            **data,
            university_id=university_id,
            created_by_id=creator_id
        )
        db.add(new_quiz)
        await db.flush()

        for q_data in questions_data:
            q_obj = QuizQuestion(quiz_id=new_quiz.id, **q_data)
            db.add(q_obj)

        await db.commit()

        # Re-fetch with selectinload and convert to dict immediately
        result = await db.execute(
            select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == new_quiz.id)
        )
        q = result.scalar_one()

        return {
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "created_by_id": q.created_by_id,
            "university_id": q.university_id,
            "created_at": q.created_at,
            "questions": [
                {
                    "id": qq.id,
                    "question_text": qq.question_text,
                    "options": qq.options,
                    "correct_option": qq.correct_option
                } for qq in q.questions
            ]
        }

    @staticmethod
    async def list_quizzes(db: AsyncSession, university_id: int) -> List[dict]:
        result = await db.execute(
            select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.university_id == university_id)
        )
        quizzes = result.scalars().all()
        return [
            {
                "id": q.id,
                "title": q.title,
                "description": q.description,
                "created_by_id": q.created_by_id,
                "university_id": q.university_id,
                "created_at": q.created_at,
                "questions": [
                    {
                        "id": qq.id,
                        "question_text": qq.question_text,
                        "options": qq.options,
                        "correct_option": qq.correct_option
                    } for qq in q.questions
                ]
            } for q in quizzes
        ]

    @staticmethod
    async def get_quiz_by_id(db: AsyncSession, quiz_id: int) -> Optional[dict]:
        result = await db.execute(
            select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
        )
        q = result.scalar_one_or_none()
        if not q:
            return None
        return {
            "id": q.id,
            "title": q.title,
            "description": q.description,
            "created_by_id": q.created_by_id,
            "university_id": q.university_id,
            "created_at": q.created_at,
            "questions": [
                {
                    "id": qq.id,
                    "question_text": qq.question_text,
                    "options": qq.options,
                    "correct_option": qq.correct_option
                } for qq in q.questions
            ]
        }

    @staticmethod
    async def submit_quiz(db: AsyncSession, user_id: int, quiz_id: int, answers_str: str) -> dict:
        result = await db.execute(
            select(Quiz).options(selectinload(Quiz.questions)).where(Quiz.id == quiz_id)
        )
        quiz = result.scalar_one_or_none()
        if not quiz:
             raise Exception("Quiz not found")

        questions = quiz.questions
        submitted_answers = json.loads(answers_str)
        correct_count = 0
        total_count = len(questions)

        for i, q in enumerate(questions):
             if i < len(submitted_answers) and submitted_answers[i] == q.correct_option:
                 correct_count += 1

        score = (correct_count / total_count * 100) if total_count > 0 else 0

        submission = QuizSubmission(
            quiz_id=quiz_id,
            user_id=user_id,
            answers=answers_str,
            score=score,
            status="completed"
        )
        db.add(submission)
        await db.commit()

        # Refetch with notes
        res = await db.execute(
            select(QuizSubmission).options(selectinload(QuizSubmission.notes)).where(QuizSubmission.id == submission.id)
        )
        s = res.scalar_one()
        return QuizSubmissionDTO.model_validate(s).model_dump()

    @staticmethod
    async def list_submissions_for_user(db: AsyncSession, user_id: int) -> List[dict]:
        result = await db.execute(
            select(QuizSubmission).options(selectinload(QuizSubmission.notes)).where(QuizSubmission.user_id == user_id)
        )
        submissions = result.scalars().all()
        return [QuizSubmissionDTO.model_validate(s).model_dump() for s in submissions]

    @staticmethod
    async def list_submissions_for_quiz(db: AsyncSession, quiz_id: int) -> List[dict]:
        result = await db.execute(
            select(QuizSubmission).options(selectinload(QuizSubmission.notes)).where(QuizSubmission.quiz_id == quiz_id)
        )
        submissions = result.scalars().all()
        return [QuizSubmissionDTO.model_validate(s).model_dump() for s in submissions]

class NoteService:
    @staticmethod
    async def create_note(db: AsyncSession, author_id: int, data: dict) -> dict:
        note = InstructorNote(author_id=author_id, **data)
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return InstructorNoteDTO.model_validate(note).model_dump()

    @staticmethod
    async def list_notes_for_student(db: AsyncSession, student_id: int) -> List[dict]:
        result = await db.execute(
            select(InstructorNote).where(InstructorNote.student_id == student_id)
        )
        notes = result.scalars().all()
        return [InstructorNoteDTO.model_validate(n).model_dump() for n in notes]
