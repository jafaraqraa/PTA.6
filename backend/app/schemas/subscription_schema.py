from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SubscriptionBase(BaseModel):
    university_id: int
    is_active: bool = True
    expires_at: Optional[datetime] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class SubscriptionDTO(SubscriptionBase):
    id: int

    class Config:
        from_attributes = True
