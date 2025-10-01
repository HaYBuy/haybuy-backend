from enum import Enum
from pydantic import BaseModel, Field , constr
from typing import Optional, Pattern
from datetime import datetime
from typing import List

class CategoryBase(BaseModel):
    name: constr = Field(min_length=2, max_length=100)
    slug: constr(pattern=r"^[a-z0-9-]+$", min_length=2, max_length=100)
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str]
    slug: Optional[str]
    parent_id: Optional[int]

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    children: List["CategoryResponse"] = []  # recursive

    class Config:
        from_attributes = True