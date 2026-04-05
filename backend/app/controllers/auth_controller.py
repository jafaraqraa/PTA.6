from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.university_service import UniversityService
from app.services.subscription_service import SubscriptionService
from app.schemas.auth_schema import LoginRequest, Token
from app.services.security_utils import get_current_university, get_domain_from_request
from app.models.enums import UserRoleEnum

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1) Extract domain and get university
    domain = get_domain_from_request(request)

    # 2) Get user by email
    user = await UserService.get_user_by_email(db, login_data.email)

    # 3) Check for super admin bypass
    if user and user.role == UserRoleEnum.SUPER_ADMIN:
        # Verify password
        if not AuthService.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )

        # Super admin bypasses all domain/university/subscription checks
        access_token = AuthService.create_access_token(
            data={
                "user_id": user.id,
                "role": user.role,
                "university_id": None
            }
        )
        return {"access_token": access_token, "token_type": "bearer"}

    # Proceed with normal domain validation for non-super-admins
    if not domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain is required"
        )

    university = await UniversityService.get_university_by_domain(db, domain)
    if not university:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"University with domain '{domain}' not found"
        )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 3) Verify password
    if not AuthService.verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    # 4) Check if user belongs to same university (except super_admin)
    if user.role != UserRoleEnum.SUPER_ADMIN:
        if user.university_id != university.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not belong to this university",
            )

        # 5) Check subscription
        if not await SubscriptionService.validate_subscription(db, university.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="University subscription has expired",
            )

    # 6) Return JWT
    access_token = AuthService.create_access_token(
        data={
            "user_id": user.id,
            "role": user.role,
            "university_id": user.university_id
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}
