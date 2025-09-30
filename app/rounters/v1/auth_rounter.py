from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from ...core.security import create_access_token, get_current_user
from ...schemas.user_schema import UserCreate, UserResponse
from typing import Annotated

fake_User_db = {
    "johndoe": {
        "id" : 1,
        "username": "johndoe",
        "password_hash": "password1",
        "full_name": "John Doe",
        "email": "johndoe@gmail.com",
        "is_active": True,
        "created_at": "2025-09-16T18:10:40.376324+07:00",
        "updated_at": "2025-09-16T18:10:40.376324+07:00",
        "deleted_at": None,
        "last_login": None,
    },
    "alice": {
        "id" : 2,
        "username": "alice",
        "password_hash": "password2",
        "full_name": "Alice Wonderland",
        "email": "alice@gmail.com",
        "is_active": True,
        "created_at": "2025-09-16T18:10:40.376324+07:00",
        "updated_at": "2025-09-16T18:10:40.376324+07:00",
        "deleted_at": None,
        "last_login": None,
    },
    "user3": {
        "id" : 3,
        "username": "user3",
        "password_hash": "password3",
        "full_name": "user3",
        "email": "user3@gmail.com",
        "is_active": True,
        "created_at": "2025-09-16T18:10:40.376324+07:00",
        "updated_at": "2025-09-16T18:10:40.376324+07:00",
        "deleted_at": None,
        "last_login": None,
    },
}

rounter = APIRouter(prefix="/auth", tags=["auth"])

@rounter.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_dict = fake_User_db.get(form_data.username)
    if not user_dict :
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    if form_data.password != user_dict["password_hash"]:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(
        data={
            "sub": user_dict["username"],
            "id": user_dict["id"],
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}