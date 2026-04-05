from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from app.models.enums import UserRoleEnum

class UserBase(BaseModel):
    email: str
    full_name: str
    role: UserRoleEnum
    university_id: Optional[int] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserDTO(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
