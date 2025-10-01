from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime

from app.db.models.Users.UserProfile import UserProfile
from ...db.models.Users.User import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.security import get_current_user
from sqlalchemy.orm import Session

from app.db.database import get_db
import bcrypt

from dotenv import load_dotenv

load_dotenv()

rounter = APIRouter(prefix="/user", tags=["user"])

@rounter.get("/", response_model=list[UserResponse])
async def get_user(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.deleted_at == None).all()
    return users

@rounter.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(user_id == User.id).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="User not found")
    
    return user_db

@rounter.put("/me", response_model=UserResponse)
async def update_user(user: UserCreate, db: Session = Depends(get_db), current_user : dict = Depends(get_current_user)):
    db_user = db.query(User).filter(User.username == current_user["username"]).first()
    if not db_user :
        raise HTTPException(status_code=404 , detail="Not found")
    
    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
    db_user.full_name = user.full_name
    db_user.password = hashed_pw.decode("utf-8") 
    db_user.username = db_user.username
    db_user.email = db_user.email

    db.commit()
    db.refresh(db_user)
    return db_user

@rounter.delete("/me",)
async def delete_user(
    db: Session = Depends(get_db), 
    current_user : dict = Depends(get_current_user)
):
    user_db = db.query(User).filter(User.id == current_user["id"]).first()

    if not user_db :
        raise HTTPException(status_code=404, detail="User not found or Not have permission")
    
    user_db.is_active = False
    user_db.updated_at=datetime.now()
    user_db.deleted_at=datetime.now()
    user_db.last_login=datetime.now()

    db.commit()
    db.refresh(user_db)

    user_profile_db = db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()

    if not user_profile_db:
        raise HTTPException(status_code=404, detail="Profile not found or Not have permission")
    
    user_profile_db.deleted_at = datetime.now()
    user_profile_db.updated_at = datetime.now()

    db.commit()
    db.refresh(user_profile_db)

    return {"detail":" User and User Profile delete success "}