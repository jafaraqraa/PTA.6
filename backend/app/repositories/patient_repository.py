from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.patient import Patient, Ear, AudiogramPoint
from app.schemas.patient_schema import PatientDTO


class PatientRepository:

    @staticmethod
    async def get_profiles(db: AsyncSession):

        result = await db.execute(
            select(Patient).options(
                selectinload(Patient.ears).selectinload(Ear.audiogram_points)
            )
        )

        patients = result.scalars().all()

        return [PatientDTO.model_validate(p) for p in patients]

    @staticmethod
    async def save_patient(db: AsyncSession, dto: PatientDTO) -> PatientDTO:

        patient = Patient(
            source_type=dto.source_type,
            image_ref=dto.image_ref,
        )

        for ear_dto in dto.ears:
            ear = Ear(
                side=ear_dto.side,
                hearing_type=ear_dto.hearing_type,
                hearing_profile=ear_dto.hearing_profile,
                hearing_tags=ear_dto.hearing_tags,
            )

            for point_dto in ear_dto.audiogram_points:
                point = AudiogramPoint(
                    test_type=point_dto.test_type,
                    frequency=point_dto.frequency,
                    threshold_db=point_dto.threshold_db,
                    is_no_response=point_dto.is_no_response
                )
                ear.audiogram_points.append(point)

            patient.ears.append(ear)
        db.add(patient)

        try:
            await db.commit()
        except Exception:
            await db.rollback()
            raise

        result = await db.execute(
            select(Patient)
            .options(
                selectinload(Patient.ears).selectinload(Ear.audiogram_points)
            )
            .where(Patient.id == patient.id)
        )
        saved_patient = result.scalar_one()
        return PatientDTO.model_validate(saved_patient)
