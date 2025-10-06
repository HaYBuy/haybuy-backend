from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from ...db.database import get_db

from ...db.models.Users.UserProfile import UserProfile
from ...schemas.user_profile_schema import UserProfileBase , UserProfileCreate, UserProfileResponse

from ...core.security import get_current_user

rounter = APIRouter(prefix="/profile", tags=["profile"])

@rounter.get("/me", response_model= UserProfileResponse)
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
): 
    profile_db = db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()

    if not profile_db :
        raise HTTPException(status_code=404, detail=" Something wrong profile not found")
 
    
    return profile_db

@rounter.get("/{user_target_id}", response_model=UserProfileResponse)
async def get_target_profile(
    user_target_id : int,
    db: Session = Depends(get_db),
):
    target_profile_db = db.query(UserProfile).filter(UserProfile.user_id == user_target_id).first()
    if not target_profile_db :
        raise HTTPException(status_code=404, detail="Something wrong profile not found")
    return target_profile_db

@rounter.put("/me/editprofile", response_model=UserProfileResponse)
async def edit_my_profile(
    data : UserProfileCreate,
    db: Session = Depends(get_db),
    current_user : dict = Depends(get_current_user)
): 
    db_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()

    if not db_profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    
    db_profile.phone = data.phone
    db_profile.address_line1 = data.address_line1
    db_profile.address_line2 = data.address_line2
    db_profile.district = data.district
    db_profile.province = data.province
    db_profile.postal_code = data.postal_code
    db_profile.latitude = data.latitude
    db_profile.longitude = data.longitude
    db_profile.location_verified = data.location_verified
    db_profile.id_verified = data.id_verified

    db.commit()
    db.refresh(db_profile)
    return db_profile
    