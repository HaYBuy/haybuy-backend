from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from ...core.security import create_access_token, get_current_user
from ...db.models.Users.User import User
from .user import fake_User_db

rounter = APIRouter(prefix="/auth", tags=["auth"])

@rounter.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_User_db.get(form_data.username)
    if not user_dict or user_dict["password_hash"] != form_data.password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user_dict["username"], "role": user_dict["role"], "id": user_dict["id"]})
    return {"access_token": access_token, "token_type": "bearer"}