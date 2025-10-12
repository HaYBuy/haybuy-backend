"""User management router."""

from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models.Users.User import User
from app.db.models.Users.UserProfile import UserProfile
from app.routers.v1.auth_router import hash_password
from app.schemas.user_schema import UserCreate, UserResponse

router = APIRouter(prefix="/user", tags=["user"])


@router.get("/", response_model=list[UserResponse])
async def get_user(db: Session = Depends(get_db)):
    """
    Get all active users.

    Args:
        db: Database session

    Returns:
        List of user objects
    """
    users = db.query(User).filter(User.deleted_at.is_(None)).all()
    return users


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Get current authenticated user's information.

    Args:
        db: Database session
        current_user: Current authenticated user from JWT token

    Returns:
        User object

    Raises:
        HTTPException: If user not found
    """
    user_db = db.query(User).filter(User.id == current_user["id"]).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    return user_db


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.

    Args:
        user_id: User ID to retrieve
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: If user not found
    """
    user_db = db.query(User).filter(user_id == User.id).first()
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")

    return user_db


@router.put("/me", response_model=UserResponse)
async def update_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    Update current user's information.

    Args:
        user: User update data
        db: Database session
        current_user: Current authenticated user

    Returns:
        Updated user object

    Raises:
        HTTPException: If user not found
    """
    db_user = db.query(User).filter(User.id == current_user["id"]).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    db_user.full_name = user.full_name
    db_user.password = hash_password(user.password)
    db_user.email = user.email
    db_user.updated_at = datetime.now()

    db.commit()
    db.refresh(db_user)
    return db_user


@router.delete("/me")
async def delete_user(
    db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    """Soft delete current user and their profile."""
    user_db = db.query(User).filter(User.id == current_user["id"]).first()

    if not user_db:
        raise HTTPException(
            status_code=404, detail="User not found or insufficient permissions"
        )

    # Soft delete user
    user_db.is_active = False
    user_db.updated_at = datetime.now()
    user_db.deleted_at = datetime.now()

    db.commit()
    db.refresh(user_db)

    # Soft delete user profile
    user_profile_db = (
        db.query(UserProfile).filter(UserProfile.user_id == current_user["id"]).first()
    )

    if user_profile_db:
        user_profile_db.deleted_at = datetime.now()
        user_profile_db.updated_at = datetime.now()
        db.commit()
        db.refresh(user_profile_db)

    return {"detail": "User and user profile deleted successfully"}
