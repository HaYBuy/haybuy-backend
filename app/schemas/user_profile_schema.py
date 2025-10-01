from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserProfileBase(BaseModel):
    phone: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    district: Optional[str]
    province: Optional[str]
    postal_code: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    location_verified: Optional[bool] = False
    id_verified: Optional[bool] = False

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True