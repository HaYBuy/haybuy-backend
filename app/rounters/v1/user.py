from fastapi import APIRouter   
from datetime import datetime
from ...db.models.Users.User import User

rounter = APIRouter(prefix="/user", tags=["user"])

fake_User_db = {
    "johndoe": {
        "id": 1,
        "username": "johndoe",
        "password_hash": "password1",
        "full_name": "John Doe",
        "email": "johndoe@gmail.com",
        "is_active": True,
        "role": "user",
        "created_at": "2025-09-16T18:10:40.376324+07:00",
        "updated_at": "2025-09-16T18:10:40.376324+07:00",
        "deleted_at": None,
        "last_login": None,
    },
    "alice": {
        "id": 2,
        "username": "alice",
        "password_hash": "password2",
        "full_name": "Alice Wonderland",
        "email": "alice@gmail.com",
        "is_active": True,
        "role": "admin",
        "created_at": "2025-09-16T18:10:40.376324+07:00",
        "updated_at": "2025-09-16T18:10:40.376324+07:00",
        "deleted_at": None,
        "last_login": None,
    },
}


@rounter.get("/")
async def get_user():
    return {
        "message": "List of users",
        "users": list(fake_User_db.values()),
    }

@rounter.get("/{user_id}")
async def get_user_by_id(user_id: int):
    for user in fake_User_db.values():
        if user["id"] == user_id:
            return {
                "message": "User found",
                "user": user,
            }
    return {"error": "User not found"}

@rounter.post("/")
async def create_user(user: User):
    if user.username in fake_User_db:
        return {"error": "Username already exists"}
    user.id = len(fake_User_db) + 1
    user.created_at = datetime.now()
    user.updated_at = datetime.now()
    fake_User_db[user.username] = user.dict()
    return {
        "message": "User created successfully",
        "user": user,
    }

@rounter.put("/{user_id}")
async def update_user(user_id: int, user: User):
    for username, existing_user in fake_User_db.items():
        if existing_user["id"] == user_id:
            user.updated_at = datetime.now()
            fake_User_db[username] = user.dict()
            return {
                "message": "User updated successfully",
                "user": user,
            } 
    return {"error": "User not found"}

@rounter.delete("/{user_id}")
async def delete_user(user_id: int):
    for username, user in list(fake_User_db.items()):
        if user["id"] == user_id:
            del fake_User_db[username]
            return {"message": "User deleted successfully"}
    return {"error": "User not found"}