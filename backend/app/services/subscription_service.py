from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.subscription_repository import SubscriptionRepository

class SubscriptionService:
    @staticmethod
    async def validate_subscription(db: AsyncSession, university_id: int) -> bool:
        subscription = await SubscriptionRepository.get_active_by_university_id(db, university_id)
        return subscription is not None
