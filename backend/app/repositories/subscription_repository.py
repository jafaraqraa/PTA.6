from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.subscription import Subscription

class SubscriptionRepository:
    @staticmethod
    async def get_active_by_university_id(db: AsyncSession, university_id: int) -> Subscription | None:
        now = datetime.now(timezone.utc)
        result = await db.execute(
            select(Subscription).where(
                and_(
                    Subscription.university_id == university_id,
                    Subscription.is_active == True,
                    (Subscription.expires_at == None) | (Subscription.expires_at > now)
                )
            )
        )
        return result.scalar_one_or_none()
