from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.university_repository import UniversityRepository

class UniversityService:
    @staticmethod
    async def get_university_by_domain(db: AsyncSession, domain: str):
        return await UniversityRepository.get_by_domain(db, domain)

    @staticmethod
    async def get_university_by_id(db: AsyncSession, university_id: int):
        return await UniversityRepository.get_by_id(db, university_id)
