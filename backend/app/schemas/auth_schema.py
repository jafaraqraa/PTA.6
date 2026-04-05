from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None
    university_id: Optional[int] = None

class LoginRequest(BaseModel):
    email: str
    password: str
