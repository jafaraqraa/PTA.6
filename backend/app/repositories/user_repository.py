from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User

from typing import Sequence
from app.models.enums import UserRoleEnum

class UserRepository:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_users(
        db: AsyncSession,
        university_id: int | None = None,
        role: UserRoleEnum | None = None
    ) -> Sequence[User]:
        query = select(User)
        if university_id is not None:
            query = query.where(User.university_id == university_id)
        if role is not None:
            query = query.where(User.role == role)
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, user_data: dict) -> User:
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def update(db: AsyncSession, user_id: int, update_data: dict) -> User | None:
        user = await UserRepository.get_by_id(db, user_id)
        if not user:
            return None
        for key, value in update_data.items():
            setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user
