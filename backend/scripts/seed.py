import asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal, engine
from app.models.university import University
from app.models.user import User
from app.models.subscription import Subscription
from app.models.enums import UserRoleEnum
from app.services.auth_service import AuthService
from datetime import datetime, timedelta, timezone

async def seed_data():
    async with AsyncSessionLocal() as db:
        # 0) Clear existing data
        await db.execute(delete(Subscription))
        await db.execute(delete(User))
        await db.execute(delete(University))
        await db.commit()

        # 1) Universities
        najah = University(name="An-Najah University", domain="najah")
        hebron = University(name="Hebron University", domain="hebron")
        db.add_all([najah, hebron])
        await db.commit()
        await db.refresh(najah)
        await db.refresh(hebron)

        # 2) Subscriptions
        sub_najah = Subscription(university_id=najah.id, is_active=True)
        sub_hebron = Subscription(university_id=hebron.id, is_active=True)
        db.add_all([sub_najah, sub_hebron])

        # 3) Users
        users = [
            User(
                email="admin@system.com",
                hashed_password=AuthService.get_password_hash("admin123"),
                full_name="Super Admin",
                role=UserRoleEnum.SUPER_ADMIN,
                university_id=None
            ),
            User(
                email="admin@najah.com",
                hashed_password=AuthService.get_password_hash("123456"),
                full_name="Najah Admin",
                role=UserRoleEnum.UNIVERSITY_ADMIN,
                university_id=najah.id
            ),
            User(
                email="lab@najah.com",
                hashed_password=AuthService.get_password_hash("123456"),
                full_name="Lab Admin",
                role=UserRoleEnum.LAB_ADMIN,
                university_id=najah.id
            ),
            User(
                email="student@najah.com",
                hashed_password=AuthService.get_password_hash("123456"),
                full_name="Student",
                role=UserRoleEnum.STUDENT,
                university_id=najah.id
            )
        ]
        db.add_all(users)
        await db.commit()
        print("Demo data seeded successfully!")

if __name__ == "__main__":
    asyncio.run(seed_data())
