from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.user_service import UserService
from app.services.security_utils import get_current_user, check_role
from app.schemas.user_schema import UserDTO, UserCreate
from app.models.enums import UserRoleEnum
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UserDTO])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if current_user.role == UserRoleEnum.SUPER_ADMIN:
        return await UserService.list_users(db)
    elif current_user.role in [UserRoleEnum.UNIVERSITY_ADMIN, UserRoleEnum.LAB_ADMIN]:
        return await UserService.list_users(db, university_id=current_user.university_id)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.post("/", response_model=UserDTO)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # University Admins can only create users for their university
    if current_user.role == UserRoleEnum.UNIVERSITY_ADMIN:
        user_data.university_id = current_user.university_id
        if user_data.role not in [UserRoleEnum.LAB_ADMIN, UserRoleEnum.STUDENT]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only create Lab Admins or Students")
    elif current_user.role != UserRoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    return await UserService.create_user(db, user_data.model_dump())

@router.put("/{user_id}", response_model=UserDTO)
async def update_user(
    user_id: int,
    update_data: dict, # Simplified for brevity
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if current_user.role != UserRoleEnum.SUPER_ADMIN:
        if user.university_id != current_user.university_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit users outside your university")

    return await UserService.update_user(db, user_id, update_data)
