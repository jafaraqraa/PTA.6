from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.attempt import Attempt
from app.models.stored_threshold import StoredThreshold
from app.schemas.stored_threshold_schema import CreateStoredThresholdDTO, StoredThresholdDTO


class StoredThresholdRepository:
    INTENSITY_TOLERANCE_DB = 0.1

    @staticmethod
    async def store_threshold(db: AsyncSession, dto: CreateStoredThresholdDTO) -> StoredThresholdDTO:

        result = await db.execute(select(Attempt).where(Attempt.id == dto.attempt_id))
        attempt = result.scalars().first()

        if attempt is None:
            raise ValueError("Attempt not found")

        if attempt.session_id != dto.session_id:
            raise ValueError("Attempt does not belong to the provided session")

        if attempt.ear_side != dto.ear_side:
            raise ValueError("Attempt ear does not match the threshold slot")

        if attempt.test_type != dto.test_type:
            raise ValueError("Attempt test type does not match the threshold slot")

        if attempt.frequency != dto.frequency:
            raise ValueError("Attempt frequency does not match the threshold slot")

        if abs(float(attempt.intensity) - float(dto.threshold_db)) > StoredThresholdRepository.INTENSITY_TOLERANCE_DB:
            raise ValueError("Attempt intensity does not match the stored threshold level")

        # Make any previous thresholds for the same slot non-final
        await db.execute(
            update(StoredThreshold)
            .where(StoredThreshold.session_id == dto.session_id)
            .where(StoredThreshold.ear_side == dto.ear_side)
            .where(StoredThreshold.test_type == dto.test_type)
            .where(StoredThreshold.frequency == dto.frequency)
            .values(is_final=False)
        )
        
        threshold = StoredThreshold(
            session_id=dto.session_id,
            attempt_id=dto.attempt_id,
            ear_side=dto.ear_side,
            test_type=dto.test_type,
            frequency=dto.frequency,
            threshold_db=dto.threshold_db,
            is_no_response=dto.is_no_response,
            is_final=True,
        )

        db.add(threshold)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        await db.refresh(threshold)

        return StoredThresholdDTO.model_validate(threshold)
