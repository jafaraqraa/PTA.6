from pydantic import BaseModel
from typing import Optional

class UniversityBase(BaseModel):
    name: str
    domain: str

class UniversityCreate(UniversityBase):
    pass

class UniversityDTO(UniversityBase):
    id: int

    class Config:
        from_attributes = True
