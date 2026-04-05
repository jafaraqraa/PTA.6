from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.subscription_service import SubscriptionService
from app.services.security_utils import get_current_user, check_role
from app.schemas.subscription_schema import SubscriptionDTO, SubscriptionCreate
from app.models.enums import UserRoleEnum
from typing import List

router = APIRouter()

@router.get("/", response_model=List[SubscriptionDTO])
async def list_subscriptions(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_role([UserRoleEnum.SUPER_ADMIN]))
):
    return await SubscriptionService.list_subscriptions(db)

@router.post("/", response_model=SubscriptionDTO)
async def create_subscription(
    sub_data: SubscriptionCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_role([UserRoleEnum.SUPER_ADMIN]))
):
    return await SubscriptionService.create_subscription(db, sub_data.model_dump())
