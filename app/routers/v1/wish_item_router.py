from fastapi import APIRouter, HTTPException, Depends
from typing import List

from sqlalchemy.orm import Session

from app.db.models.items.item import Item
from app.schemas.item_schema import ItemResponse
from ...db.database import get_db

from ...db.models.items.wishItem import WishItem
from ...schemas.wish_item_schema import (
    WishItemAdd,
    WishItemResponse,
    WishPrivacy,
)

from ...core.security import get_current_user

router = APIRouter(prefix="/wish-item", tags=["wish-item"])


@router.post("/", response_model=WishItemResponse)
async def add_wish_item(
    wish: WishItemAdd,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    existing_wish_item_db = (
        db.query(WishItem)
        .filter(
            WishItem.item_id == wish.item_id, WishItem.user_id == current_user["id"]
        )
        .first()
    )

    if existing_wish_item_db:
        raise HTTPException(status_code=403, detail="item already in wish list")

    db_wish = WishItem(user_id=current_user["id"], item_id=wish.item_id)

    db.add(db_wish)
    db.commit()
    db.refresh(db_wish)
    return db_wish


@router.delete("/my/{wish_id}")
async def remove_wish_item(
    wish_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    db_wish_item = (
        db.query(WishItem)
        .filter(WishItem.id == wish_id, WishItem.user_id == current_user["id"])
        .first()
    )
    if not db_wish_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db.delete(db_wish_item)
    db.commit()
    return {"detail": "Wish item deleted"}


@router.patch("/my/{wish_id}/privacy", response_model=WishItemResponse)
async def set_privacy_wish_list(
    wish_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    wish = db.query(WishItem).filter(WishItem.id == wish_id).first()
    if not wish:
        raise HTTPException(status_code=404, detail="Wish item not found")

    if wish.user_id != current_user["id"]:
        raise HTTPException(status_code=403, detail="Not allowed to change privacy")

    if wish.privacy == "private":
        wish.privacy = "public"
    else:
        wish.privacy = "private"

    db.commit()
    db.refresh(wish)
    return wish


@router.get("/my/items", response_model=List[ItemResponse])
async def get_my_wish_list(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    items = (
        db.query(Item)
        .join(WishItem, Item.id == WishItem.item_id)
        .filter(WishItem.user_id == current_user["id"])
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items


@router.get("/my", response_model=List[WishItemResponse])
async def get_my_wish_list(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    wish_list = (
        db.query(WishItem)
        .filter(WishItem.user_id == current_user["id"])
        .offset(skip)
        .limit(limit)
        .all()
    )
    return wish_list


@router.get("/my/share/{target_id}", response_model=List[WishItemResponse])
async def share_my_wish_List(
    target_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    wish_items_db = (
        db.query(WishItem)
        .filter(
            WishItem.user_id == target_id, WishItem.privacy == WishPrivacy.PUBLIC.value
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return wish_items_db
