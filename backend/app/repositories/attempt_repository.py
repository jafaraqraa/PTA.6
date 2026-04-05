from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.attempt import Attempt
from app.schemas.attempt_schema import AttemptDTO, AttemptCreateDTO


class AttemptRepository:

    @staticmethod
    async def create_attempt(db: AsyncSession, dto: AttemptCreateDTO) -> AttemptDTO:

        attempt = Attempt(
            session_id=dto.session_id,
            ear_side=dto.ear_side,
            test_type=dto.test_type,
            frequency=dto.frequency,
            intensity=dto.intensity,
            masking_level_db=dto.masking_level_db,
            response=dto.response
        )

        db.add(attempt)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        await db.refresh(attempt)

        return AttemptDTO.model_validate(attempt)

    @staticmethod
    async def get_attempts_by_session(db: AsyncSession, session_id: int) -> list[AttemptDTO]:
        result = await db.execute(
            select(Attempt)
            .where(Attempt.session_id == session_id)
            .order_by(Attempt.created_at.asc())
        )
        attempts = result.scalars().all()
        return [AttemptDTO.model_validate(a) for a in attempts]
