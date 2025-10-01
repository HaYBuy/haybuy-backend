from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from ...db.database import get_db

from ...db.models.items.wishItem import WishItem
from ...schemas.wish_item_schema import WishItemBase, WishItemCreate, WishItemResponse, WishPrivacy

from ...core.security import get_current_user

rounter = APIRouter(prefix="/wish-item", tags=["wish-item"])

@rounter.post("/", response_model=WishItemResponse)
async def add_wish_item(
    wish: WishItemCreate,
    db : Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_wish = WishItem(
        user_id = current_user["id"],
        item_id = wish.item_id
    )

    db.add(db_wish)
    db.commit()
    db.refresh(db_wish)
    return db_wish

@rounter.delete("/my/{item_id}")
async def remove_wish_item(
    item_id: int,
    db : Session = Depends(get_db),
    current_user: dict = Depends(get_current_user) 
):
    db_wish_item = db.query(WishItem).filter(WishItem.id == item_id, WishItem.user_id == current_user["id"]).first()
    if not db_wish_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_wish_item)
    db.commit()
    return {"detail": "Wish item deleted"}

@rounter.patch("/my/{wish_id}/privacy", response_model=WishItemResponse)
async def set_privacy_wish_list(
    wish_id : int,
    privacy : str,
    db : Session = Depends(get_db),
    current_user : dict = Depends(get_current_user)
): 
    if privacy not in [p.value for p in WishPrivacy ]:
        raise HTTPException(status_code=400, detail="Invalid Privacy")
    
    db_wish = db.query(WishItem).filter(WishItem.id == wish_id, WishItem.user_id == current_user["id"]).first()  
    if not db_wish:
        raise HTTPException(status_code=404, detail="Item not found")

    db_wish.privacy = privacy
    db.commit()
    db.refresh(db_wish)
    return db_wish

@rounter.get("/my", response_model=List[WishItemResponse])
async def get_my_wish_list(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user : dict = Depends(get_current_user)
):
    wish_list = db.query(WishItem).filter(WishItem.user_id == current_user["id"]).offset(skip).limit(limit).all()
    return wish_list

# @rounter.get("/my/share", response_model=List[WishItemResponse])
# async def share_my_wish_List(
#     skip : int = 0,
#     limit : int = 10,
#     db: Session = Depends(get_db),
    
# )
