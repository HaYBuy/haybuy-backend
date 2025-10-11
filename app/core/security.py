"""Security utilities for authentication and authorization."""

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

# Constants with secure defaults
DEFAULT_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/token")


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.

    Args:
        data: Dictionary containing user data to encode in the token

    Returns:
        Encoded JWT token string

    Raises:
        ValueError: If required environment variables are missing
    """
    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise ValueError("JWT_SECRET_KEY environment variable is required")

    algorithm = os.getenv("JWT_ALGORITHM", DEFAULT_ALGORITHM)
    expire_minutes = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", DEFAULT_TOKEN_EXPIRE_MINUTES)
    )

    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current authenticated user from JWT token.

    Args:
        db: Database session
        token: JWT token from Authorization header

    Returns:
        User object if authentication is successful

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    secret_key = os.getenv("JWT_SECRET_KEY")
    if not secret_key:
        raise ValueError("JWT_SECRET_KEY environment variable is required")

    algorithm = os.getenv("JWT_ALGORITHM", DEFAULT_ALGORITHM)

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise HTTPException(status_code=401, detail="Invalid or inactive user")

        return {"username": username, "id": id}
    except JWTError:
        raise credentials_exception
