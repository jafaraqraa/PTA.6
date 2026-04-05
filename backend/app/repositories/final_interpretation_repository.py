from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, select

from app.models.final_interpretation import FinalInterpretation
from app.schemas.final_interpretation_schema import FinalInterpretationCreateDTO, FinalInterpretationDTO
from app.services.final_interpretation_builder import FinalInterpretationBuilder


class FinalInterpretationRepository:
    @staticmethod
    async def replace_for_session(
        db: AsyncSession,
        session_id: int,
        interpretations: list[FinalInterpretationCreateDTO],
    ) -> list[FinalInterpretationDTO]:
        await db.execute(
            delete(FinalInterpretation).where(FinalInterpretation.session_id == session_id)
        )

        created_models: list[FinalInterpretation] = []
        for item in interpretations:
            generated_comment = FinalInterpretationBuilder.build_clinical_comment(item)
            model = FinalInterpretation(
                session_id=session_id,
                ear_side=item.ear_side,
                overall_type=item.overall_type,
                severity=item.severity,
                configuration=item.configuration,
                affected_frequencies_hz=item.affected_frequencies_hz,
                clinical_comment=generated_comment,
            )
            db.add(model)
            created_models.append(model)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        for model in created_models:
            await db.refresh(model)

        return [FinalInterpretationDTO.model_validate(model) for model in created_models]

    @staticmethod
    async def get_for_session(db: AsyncSession, session_id: int) -> list[FinalInterpretationDTO]:
        result = await db.execute(
            select(FinalInterpretation)
            .where(FinalInterpretation.session_id == session_id)
            .order_by(FinalInterpretation.ear_side.asc())
        )
        items = result.scalars().all()
        return [FinalInterpretationDTO.model_validate(item) for item in items]
