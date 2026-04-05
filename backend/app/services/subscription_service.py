from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.subscription_repository import SubscriptionRepository

class SubscriptionService:
    @staticmethod
    async def validate_subscription(db: AsyncSession, university_id: int) -> bool:
        subscription = await SubscriptionRepository.get_active_by_university_id(db, university_id)
        return subscription is not None

    @staticmethod
    async def list_subscriptions(db: AsyncSession):
        return await SubscriptionRepository.list_subscriptions(db)

    @staticmethod
    async def create_subscription(db: AsyncSession, subscription_data: dict):
        return await SubscriptionRepository.create(db, subscription_data)

    @staticmethod
    async def update_subscription(db: AsyncSession, subscription_id: int, update_data: dict):
        return await SubscriptionRepository.update(db, subscription_id, update_data)
