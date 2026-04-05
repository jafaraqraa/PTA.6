from fastapi import Request, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.auth_service import SECRET_KEY, ALGORITHM
from app.services.user_service import UserService
from app.services.university_service import UniversityService
from app.schemas.auth_schema import TokenData
from app.models.enums import UserRoleEnum

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_university(request: Request, db: AsyncSession = Depends(get_db)):
    host = request.headers.get("host", "")
    domain = host.split(".")[0]

    # Fallback to query param for testing
    if domain in ["localhost", "127", ""]:
        domain = request.query_params.get("domain")

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

    return university

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(
            user_id=user_id,
            role=payload.get("role"),
            university_id=payload.get("university_id")
        )
    except JWTError:
        raise credentials_exception

    user = await UserService.get_user_by_id(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

def check_role(allowed_roles: list[UserRoleEnum]):
    async def role_checker(current_user = Depends(get_current_user)):
        if current_user.role == UserRoleEnum.SUPER_ADMIN:
            return current_user
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        return current_user
    return role_checker

def enforce_multi_tenancy(user, university_id: int):
    if user.role == UserRoleEnum.SUPER_ADMIN:
        return
    if user.university_id != university_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: University mismatch"
        )
