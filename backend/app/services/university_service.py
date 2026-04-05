from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.university_repository import UniversityRepository

class UniversityService:
    @staticmethod
    async def get_university_by_domain(db: AsyncSession, domain: str):
        return await UniversityRepository.get_by_domain(db, domain)

    @staticmethod
    async def get_university_by_id(db: AsyncSession, university_id: int):
        return await UniversityRepository.get_by_id(db, university_id)

    @staticmethod
    async def list_universities(db: AsyncSession):
        return await UniversityRepository.list_universities(db)

    @staticmethod
    async def create_university(db: AsyncSession, university_data: dict):
        return await UniversityRepository.create(db, university_data)

    @staticmethod
    async def update_university(db: AsyncSession, university_id: int, update_data: dict):
        return await UniversityRepository.update(db, university_id, update_data)
