"""User profile schema definitions."""

from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class UserProfileBase(BaseModel):
    """Base user profile model with common fields."""

    phone: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    district: Optional[str] = None
    province: Optional[str] = None
    postal_code: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_verified: Optional[bool] = False
    id_verified: Optional[bool] = False


class UserProfileCreate(UserProfileBase):
    """Schema for creating a new user profile."""


class UserProfileResponse(UserProfileBase):
    id: int
    user_id: int
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
