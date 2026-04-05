from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.university import University

class UniversityRepository:
    @staticmethod
    async def get_by_domain(db: AsyncSession, domain: str) -> University | None:
        result = await db.execute(select(University).where(University.domain == domain))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, university_id: int) -> University | None:
        result = await db.execute(select(University).where(University.id == university_id))
        return result.scalar_one_or_none()
