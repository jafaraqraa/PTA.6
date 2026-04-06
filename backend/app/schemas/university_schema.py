from pydantic import BaseModel
from typing import Optional

class UniversityBase(BaseModel):
    name: str

class UniversityCreate(UniversityBase):
    pass

class UniversityUpdate(BaseModel):
    name: Optional[str] = None

class UniversityDTO(UniversityBase):
    id: int

    class Config:
        from_attributes = True
