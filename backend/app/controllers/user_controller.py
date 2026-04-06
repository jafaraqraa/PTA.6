from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.user_service import UserService
from app.services.security_utils import get_current_user, check_role
from app.schemas.user_schema import UserDTO, UserCreate, UserUpdate
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
    elif current_user.role == UserRoleEnum.UNIVERSITY_ADMIN:
        return await UserService.list_users(db, university_id=current_user.university_id)
    elif current_user.role == UserRoleEnum.LAB_ADMIN:
        return await UserService.list_users(db, university_id=current_user.university_id, role=UserRoleEnum.STUDENT)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

@router.post("/", response_model=UserDTO)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # Enforce role-based creation rules
    if current_user.role == UserRoleEnum.UNIVERSITY_ADMIN:
        # University Admin can only create users for their own university
        user_data.university_id = current_user.university_id
        if user_data.role not in [UserRoleEnum.LAB_ADMIN, UserRoleEnum.STUDENT]:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only create Lab Admins or Students")
    elif current_user.role == UserRoleEnum.LAB_ADMIN:
        # Lab Admin can only create Students for their university
        user_data.university_id = current_user.university_id
        if user_data.role != UserRoleEnum.STUDENT:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Can only create Students")
    elif current_user.role != UserRoleEnum.SUPER_ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to create users")

    return await UserService.create_user(db, user_data.model_dump())

@router.put("/{user_id}", response_model=UserDTO)
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Enforce role-based update rules
    if current_user.role == UserRoleEnum.SUPER_ADMIN:
        pass # Full access
    elif current_user.role == UserRoleEnum.UNIVERSITY_ADMIN:
        if user.university_id != current_user.university_id:
            raise HTTPException(status_code=403, detail="Not authorized to edit users outside your university")
        # Cannot promote to Super Admin or move user to another university
        if update_data.role == UserRoleEnum.SUPER_ADMIN:
            raise HTTPException(status_code=403, detail="Cannot promote to Super Admin")
        if update_data.university_id and update_data.university_id != current_user.university_id:
            raise HTTPException(status_code=403, detail="Cannot change university")
    elif current_user.role == UserRoleEnum.LAB_ADMIN:
        if user.university_id != current_user.university_id or user.role != UserRoleEnum.STUDENT:
            raise HTTPException(status_code=403, detail="Can only edit students in your university")
    else:
        raise HTTPException(status_code=403, detail="Not authorized to update users")

    return await UserService.update_user(db, user_id, update_data.model_dump(exclude_unset=True))
