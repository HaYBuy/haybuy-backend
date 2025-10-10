from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...db.models.Categorys.main import Category
from ...schemas.category_schema import CategoryChainResponse, CategoryCreate, CategoryResponse, CategoryUpdate
from ...core.security import get_current_user


rounter = APIRouter(prefix="/category", tags=["category"])


@rounter.post("/", response_model=CategoryResponse)
async def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
):
    
    existing_cate = db.query(Category).filter(Category.name == category.name).first()
    if existing_cate :
        raise HTTPException(status_code=409, detail="Category name already exists")


    if category.parent_id is not None and category.parent_id != 0:
        existing_parent = db.query(Category).filter(Category.id == category.parent_id).first()
        if not existing_parent:
            raise HTTPException(status_code=404, detail="Parent category not found")
        
    db_category = Category(
        name=category.name,
        slug=category.slug,
        parent_id=category.parent_id or None
    )
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@rounter.get("/", response_model=List[CategoryResponse])
async def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return db.query(Category).offset(skip).limit(limit).all()


@rounter.get("/{category_id}", response_model=CategoryChainResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@rounter.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category_update.name is not None:
        category.name = category_update.name
    if category_update.slug is not None:
        category.slug = category_update.slug
    if category_update.parent_id is not None:
        category.parent_id = category_update.parent_id

    db.commit()
    db.refresh(category)
    return category


@rounter.delete("/{category_id}", response_model=dict)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    db.delete(category)
    db.commit()
    return {"detail": "Category deleted successfully"}
