from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.analytics_service import AnalyticsService
from app.services.security_utils import get_current_user
from app.models.enums import UserRoleEnum

router = APIRouter()

@router.get("/")
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role == UserRoleEnum.SUPER_ADMIN:
        return await AnalyticsService.get_super_admin_stats(db)
    elif current_user.role == UserRoleEnum.UNIVERSITY_ADMIN:
        return await AnalyticsService.get_university_admin_stats(db, current_user.university_id)
    elif current_user.role == UserRoleEnum.LAB_ADMIN:
        return await AnalyticsService.get_lab_admin_stats(db, current_user.university_id, current_user.id)
    elif current_user.role == UserRoleEnum.STUDENT:
        return await AnalyticsService.get_student_stats(db, current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Not authorized")
