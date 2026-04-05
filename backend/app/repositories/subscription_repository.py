from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
from app.models.subscription import Subscription

from typing import Sequence

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

    @staticmethod
    async def get_by_id(db: AsyncSession, subscription_id: int) -> Subscription | None:
        result = await db.execute(select(Subscription).where(Subscription.id == subscription_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_subscriptions(db: AsyncSession) -> Sequence[Subscription]:
        result = await db.execute(select(Subscription))
        return result.scalars().all()

    @staticmethod
    async def create(db: AsyncSession, subscription_data: dict) -> Subscription:
        subscription = Subscription(**subscription_data)
        db.add(subscription)
        await db.commit()
        await db.refresh(subscription)
        return subscription

    @staticmethod
    async def update(db: AsyncSession, subscription_id: int, update_data: dict) -> Subscription | None:
        subscription = await SubscriptionRepository.get_by_id(db, subscription_id)
        if not subscription:
            return None
        for key, value in update_data.items():
            setattr(subscription, key, value)
        await db.commit()
        await db.refresh(subscription)
        return subscription
