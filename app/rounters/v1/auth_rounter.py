from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models.Users.User import User
from ...core.security import create_access_token, get_current_user
from ...schemas.user_schema import UserCreate, UserResponse
from app.db.models.Users.UserProfile import UserProfile
from typing import Annotated
import bcrypt

from sqlalchemy.orm import Session

rounter = APIRouter(prefix="/auth", tags=["auth"])

class LoginRequest(BaseModel):
    username: str
    password: str

@rounter.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    hashed_pw = bcrypt.hashpw(form_data.password.encode(), bcrypt.gensalt())
    user_db = db.query(User).filter(User.username == form_data.username).first()
    if not user_db :
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    if not bcrypt.checkpw(form_data.password.encode("utf-8"), user_db.password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(
        data={
            "sub": user_db.username,
            "id": user_db.id,
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}

@rounter.post("/login")
async def login_for_access_token(data: LoginRequest, db: Session = Depends(get_db)):
    user_db = db.query(User).filter(User.username == data.username).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    if not bcrypt.checkpw(data.password.encode("utf-8"), user_db.password.encode("utf-8")):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(
        data={ 
            "username": user_db.username,
            "id": user_db.id,
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


@rounter.post("/register" , response_model=UserResponse)
async def create_user(user: UserCreate , db : Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail=f"User already exists"
        )
    
    hashed_pw = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())

    new_user = User(
        username=user.username,
        password=hashed_pw.decode("utf-8") ,
        full_name=user.full_name,
        email=user.email,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        deleted_at=None,
        last_login=None,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    new_user_profile = UserProfile(
        user_id = new_user.id
    )

    db.add(new_user_profile)
    db.commit()
    db.refresh(new_user_profile)

    return new_user

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