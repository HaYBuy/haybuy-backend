"""Category schema definitions."""

from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime
from typing import List


class CategoryBase(BaseModel):
    """Base category model with common fields."""

    name: Annotated[str, Field(min_length=2, max_length=100)]
    slug: Annotated[str, Field(pattern=r"^[a-z0-9-]+$", min_length=2, max_length=100)]
    parent_id: Optional[int] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""


class CategoryUpdate(BaseModel):
    """Schema for updating an existing category."""

    name: Optional[str] = None
    slug: Optional[str] = None
    parent_id: Optional[int] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    children: List["CategoryResponse"] = []  # recursive

    class Config:
        from_attributes = True


class CategoryChainResponse(CategoryBase):
    id: int
    children: List["CategoryChainResponse"] = []

    class Config:
        from_attributes = True
