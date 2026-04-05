from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.university_service import UniversityService
from app.services.security_utils import get_current_user, check_role
from app.schemas.university_schema import UniversityDTO, UniversityCreate
from app.models.enums import UserRoleEnum
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UniversityDTO])
async def list_universities(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_role([UserRoleEnum.SUPER_ADMIN]))
):
    return await UniversityService.list_universities(db)

@router.post("/", response_model=UniversityDTO)
async def create_university(
    university_data: UniversityCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_role([UserRoleEnum.SUPER_ADMIN]))
):
    return await UniversityService.create_university(db, university_data.model_dump())

@router.get("/{university_id}", response_model=UniversityDTO)
async def get_university(
    university_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # University Admins can only view their own university
    if current_user.role != UserRoleEnum.SUPER_ADMIN:
        if university_id != current_user.university_id:
            raise HTTPException(status_code=403, detail="Not authorized")

    return await UniversityService.get_university_by_id(db, university_id)
