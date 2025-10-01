from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from ...db.models.Users.User import User
from app.schemas.user_schema import UserCreate, UserResponse
from app.core.security import get_current_user
from sqlalchemy.orm import Session

from app.db.database import get_db
import bcrypt

from dotenv import load_dotenv

load_dotenv()

rounter = APIRouter(prefix="/user", tags=["user"])

fake_User_db = {
    "johndoe": {
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
}


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
    db_user = db.query(User).filter(User.id == current_user["id"])
    if not db_user :
        raise HTTPException(status_code=404 , detail="Not found")
    
    db_user.full_name = user.full_name


    for username, existing_user in fake_User_db.items():
        if existing_user["id"] == user_id:
            update_user = User(
                username=user.username,
                password_hash=user.password_hash,
                full_name=user.full_name,
                email=user.email,
                is_active=True,
                id=fake_User_db[username]["id"],
                created_at=fake_User_db[username]["created_at"],
                updated_at=datetime.now(),
                deleted_at=None,
                last_login=None,
            )
            fake_User_db[username] = update_user.dict()
            return update_user
    raise HTTPException(status_code=404, detail="User not found")

@rounter.delete("/{user_id}", response_model=UserResponse)
async def delete_user(user_id: int):
    for username, user in list(fake_User_db.items()):
        if user["id"] == user_id:
            delete_user = User(
                username= fake_User_db[username]["username"],
                password_hash=fake_User_db[username]["password_hash"],
                full_name=fake_User_db[username]["full_name"],
                email=fake_User_db[username]["email"],
                id=fake_User_db[username]["id"],
                created_at=fake_User_db[username]["created_at"],
                is_active=False,
                updated_at=datetime.now(),
                deleted_at=datetime.now(),
                last_login=None,
            )
            fake_User_db[username] = delete_user.dict()
            return delete_user
    raise HTTPException(status_code=404, detail="User not found")