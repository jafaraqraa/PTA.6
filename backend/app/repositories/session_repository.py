from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone

from app.models.session import Session as SessionModel
from app.models.patient import Patient, Ear
from app.schemas.session_schema import SessionCreateDTO, SessionDTO, SessionFullDTO, SessionWithPatientDTO


class SessionRepository:

    @staticmethod
    async def create_session(db: AsyncSession, dto: SessionCreateDTO) -> SessionDTO:

        session = SessionModel(
            user_id=dto.user_id,
            patient_id=dto.patient_id
        )

        db.add(session)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        await db.refresh(session)

        return SessionDTO.model_validate(session)

    @staticmethod
    async def get_session(db: AsyncSession, session_id: int) -> SessionDTO | None:

        result = await db.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )

        session = result.scalar_one_or_none()

        if not session:
            return None

        return SessionDTO.model_validate(session)

    @staticmethod
    async def get_session_with_patient(db: AsyncSession, session_id: int) -> SessionWithPatientDTO | None:

        result = await db.execute(
            select(SessionModel)
            .options(
                selectinload(SessionModel.patient)
                .selectinload(Patient.ears)
                .selectinload(Ear.audiogram_points)
            )
            .where(SessionModel.id == session_id)
        )

        session = result.scalar_one_or_none()

        if not session:
            return None

        return SessionWithPatientDTO.model_validate(session)

    @staticmethod
    async def get_full_session(db: AsyncSession, session_id: int) -> SessionFullDTO | None:

        result = await db.execute(
            select(SessionModel)
            .options(
                selectinload(SessionModel.patient)
                .selectinload(Patient.ears)
                .selectinload(Ear.audiogram_points)
            )
            .options(selectinload(SessionModel.attempts))
            .options(selectinload(SessionModel.stored_thresholds))
            .options(selectinload(SessionModel.final_interpretations))
            .where(SessionModel.id == session_id)
        )

        session = result.scalar_one_or_none()

        if not session:
            return None

        return SessionFullDTO.model_validate(session)

    @staticmethod
    async def mark_session_ended(db: AsyncSession, session_id: int) -> SessionDTO | None:

        result = await db.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        session = result.scalar_one_or_none()

        if not session:
            return None

        if session.end_time is None:
            session.end_time = datetime.now(timezone.utc)

            try:
                await db.commit()
            except Exception:
                await db.rollback()
                raise

            await db.refresh(session)

        return SessionDTO.model_validate(session)
