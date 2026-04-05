from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.university_service import UniversityService
from app.services.subscription_service import SubscriptionService
from app.schemas.auth_schema import LoginRequest, Token
from app.services.security_utils import get_current_university
from app.models.enums import UserRoleEnum

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    # 1) Extract domain and get university
    host = request.headers.get("host", "")
    # Robustly handle host with port (e.g. najah.localhost:8000)
    host_parts = host.split(":")[0].split(".")

    # If the first part is 'localhost' or an IP, it's not a subdomain
    if host_parts[0] in ["localhost", "127", ""] or host_parts[0].isdigit():
        domain = request.query_params.get("domain")
        # Special case: allow extracting from custom header if frontend sends it
        if not domain:
            domain = request.headers.get("X-University-Domain")
    else:
        domain = host_parts[0]

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

    # 2) Get user by email
    user = await UserService.get_user_by_email(db, login_data.email)
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
