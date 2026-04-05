from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository

from app.models.enums import UserRoleEnum
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        return await UserRepository.get_by_email(db, email)

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: int):
        return await UserRepository.get_by_id(db, user_id)

    @staticmethod
    async def list_users(db: AsyncSession, university_id: int | None = None, role: UserRoleEnum | None = None):
        return await UserRepository.list_users(db, university_id, role)

    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict):
        if "password" in user_data:
            user_data["hashed_password"] = pwd_context.hash(user_data.pop("password"))
        return await UserRepository.create(db, user_data)

    @staticmethod
    async def update_user(db: AsyncSession, user_id: int, update_data: dict):
        if "password" in update_data:
            update_data["hashed_password"] = pwd_context.hash(update_data.pop("password"))
        return await UserRepository.update(db, user_id, update_data)
