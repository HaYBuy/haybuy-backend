from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from app.db.models.Users.User import User
from sqlalchemy.orm import Session
from app.db.database import get_db

load_dotenv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM"))
    return encoded_jwt

def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            os.getenv("JWT_SECRET_KEY"), 
            algorithms=[os.getenv("JWT_ALGORITHM")]
        )


        username: str = payload.get("sub")
        id : int = payload.get("id")

        if username is None or id is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid or inactive user")

        return {"username": username, "id": id}
    except JWTError:
        raise credentials_exception
    

