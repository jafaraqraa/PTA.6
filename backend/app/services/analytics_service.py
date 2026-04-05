from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.user import User
from app.models.university import University
from app.models.subscription import Subscription
from app.models.session import Session
from app.models.enums import UserRoleEnum
from datetime import datetime, timezone

class AnalyticsService:
    @staticmethod
    async def get_super_admin_stats(db: AsyncSession):
        total_universities = await db.execute(select(func.count(University.id)))
        total_users = await db.execute(select(func.count(User.id)))
        total_students = await db.execute(select(func.count(User.id)).where(User.role == UserRoleEnum.STUDENT))

        now = datetime.now(timezone.utc)
        active_subscriptions = await db.execute(
            select(func.count(Subscription.id)).where(
                Subscription.is_active == True,
                (Subscription.expires_at == None) | (Subscription.expires_at > now)
            )
        )

        return {
            "total_universities": total_universities.scalar(),
            "total_users": total_users.scalar(),
            "total_students": total_students.scalar(),
            "active_subscriptions": active_subscriptions.scalar()
        }

    @staticmethod
    async def get_university_admin_stats(db: AsyncSession, university_id: int):
        total_students = await db.execute(
            select(func.count(User.id)).where(
                User.university_id == university_id,
                User.role == UserRoleEnum.STUDENT
            )
        )
        total_lab_admins = await db.execute(
            select(func.count(User.id)).where(
                User.university_id == university_id,
                User.role == UserRoleEnum.LAB_ADMIN
            )
        )
        total_sessions = await db.execute(
            select(func.count(Session.id))
            .join(User, Session.user_id == User.id)
            .where(User.university_id == university_id)
        )

        return {
            "total_students": total_students.scalar(),
            "total_lab_admins": total_lab_admins.scalar(),
            "total_sessions": total_sessions.scalar(),
            "avg_performance": 85 # Placeholder
        }

    @staticmethod
    async def get_student_stats(db: AsyncSession, user_id: int):
        total_sessions = await db.execute(
            select(func.count(Session.id)).where(Session.user_id == user_id)
        )
        completed_sessions = await db.execute(
            select(func.count(Session.id)).where(
                Session.user_id == user_id,
                Session.end_time != None
            )
        )

        return {
            "total_sessions": total_sessions.scalar(),
            "completed": completed_sessions.scalar(),
            "avg_performance": 78, # Placeholder
            "last_performance": 90 # Placeholder
        }
