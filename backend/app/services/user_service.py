from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository

class UserService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        return await UserRepository.get_by_email(db, email)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        return await UserRepository.get_by_id(db, user_id)
