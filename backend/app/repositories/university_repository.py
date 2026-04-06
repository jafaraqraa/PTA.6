from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.university import University

from typing import Sequence

class UniversityRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, university_id: int) -> University | None:
        result = await db.execute(select(University).where(University.id == university_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_universities(db: AsyncSession) -> Sequence[University]:
        result = await db.execute(select(University))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, university_data: dict) -> University:
        university = University(**university_data)
        db.add(university)
        await db.commit()
        await db.refresh(university)
        return university

    @staticmethod
    async def update(db: AsyncSession, university_id: int, update_data: dict) -> University | None:
        university = await UniversityRepository.get_by_id(db, university_id)
        if not university:
            return None
        for key, value in update_data.items():
            setattr(university, key, value)
        await db.commit()
        await db.refresh(university)
        return university
