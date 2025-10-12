"""Authentication router for user login and registration."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel

from app.db.database import get_db
from app.db.models.Users.User import User
from ...core.security import create_access_token
from ...schemas.user_schema import UserCreate, UserResponse
from app.db.models.Users.UserProfile import UserProfile
from typing import Annotated
import bcrypt

from sqlalchemy.orm import Session

# Security constants
BCRYPT_SALT_ROUNDS = 12

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    """Login request model."""

    username: str
    password: str


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt with secure salt rounds.

    Args:
        password: Plain text password to hash

    Returns:
        Hashed password string
    """
    hashed = bcrypt.hashpw(
        password.encode("utf-8"), bcrypt.gensalt(rounds=BCRYPT_SALT_ROUNDS)
    )
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against

    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
):
    """
    OAuth2 compatible token login endpoint.

    Args:
        form_data: OAuth2 password request form with username and password
        db: Database session

    Returns:
        Dictionary with access_token and token_type

    Raises:
        HTTPException: If credentials are invalid
    """
    # Validate empty credentials
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=422,
            detail=[
                {
                    "loc": [
                        "body",
                        "username" if not form_data.username else "password",
                    ],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ],
        )

    user_db = db.query(User).filter(User.username == form_data.username).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not verify_password(form_data.password, user_db.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(
        data={
            "sub": user_db.username,
            "id": user_db.id,
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
async def login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Alternative login endpoint with JSON body.

    Args:
        data: Login request with username and password
        db: Database session

    Returns:
        Dictionary with access_token and token_type

    Raises:
        HTTPException: If credentials are invalid
    """
    user_db = db.query(User).filter(User.username == data.username).first()
    if not user_db:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not verify_password(data.password, user_db.password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    access_token = create_access_token(
        data={
            "username": user_db.username,
            "id": user_db.id,
        }
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Args:
        user: User creation data
        db: Database session

    Returns:
        Created user object

    Raises:
        HTTPException: If username already exists
    """
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_pw = hash_password(user.password)

    new_user = User(
        username=user.username,
        password=hashed_pw,
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

    new_user_profile = UserProfile(user_id=new_user.id)

    db.add(new_user_profile)
    db.commit()
    db.refresh(new_user_profile)

    return new_user
