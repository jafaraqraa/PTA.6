from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.university_service import UniversityService
from app.services.subscription_service import SubscriptionService
from app.schemas.auth_schema import LoginRequest, Token
from app.models.enums import UserRoleEnum

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1) Get user by email
    user = await UserService.get_user_by_email(db, login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 2) Verify password
    if not AuthService.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 3) Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    # 4) Subscription Check (except for Super Admin)
    if user.role != UserRoleEnum.SUPER_ADMIN:
        if not user.university_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not assigned to any university",
            )

        if not await SubscriptionService.validate_subscription(db, user.university_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="University subscription has expired",
            )

    # 5) Return JWT
    access_token = AuthService.create_access_token(
        data={
            "user_id": user.id,
            "role": user.role,
            "university_id": user.university_id
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}
