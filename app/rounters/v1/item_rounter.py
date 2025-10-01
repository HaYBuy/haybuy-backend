from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from ...db.database import get_db

from ...db.models.items.item import Item
from ...schemas.item_schema import ItemCreate, ItemResponse, ItemStatus
from app.db.models.PriceHistorys.main import PriceHistory
from app.schemas.price_history import PriceHistoryCreate, PriceHistoryResponse

from ...core.security import get_current_user

rounter = APIRouter(prefix="/item", tags=["item"])  


#1. ดึง item ไปแสดงหน้า home ดึงสินค้ามาทั้งหมด + pagination
#2. ดึง item ไปแสดงหน้า shop ดึงสินค้าตามหมวดหมู่ + pagination
#3. ดึง item ไปแสดงหน้า detail ดึงสินค้าตาม id
#4. ดึง item ไปแสดงแบบ search + filter + pagination
#5. ดึง item ของตัวเอง (ร้านของตัวเอง) + pagination
#6. สร้าง item (ร้านของตัวเอง)
#7. แก้ไข item (ร้านของตัวเอง)
#8. ลบ item (ร้านของตัวเอง) - soft delete
#9. เปลี่ยนสถานะ item (ร้านของตัวเอง) - available, out of stock, discontinued
#10. อัพโหลดรูป item (ร้านของตัวเอง) - ใช้ Cloudinary

# get item by search + filter + pagination
@rounter.get("/", response_model=List[ItemResponse])
async def list_items(
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    category_id: Optional[int] = None,
    
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    q = db.query(Item)
    
    if search:
        q = q.filter(Item.name.ilike(f"%{search}%"))
    if category_id is not None:
        q = q.filter(Item.category_id == category_id)
    if min_price is not None: 
        q = q.filter(Item.price >= min_price)
    if max_price is not None:
        q = q.filter(Item.price <= max_price)
    
    items = q.offset(skip).limit(limit).all()
    return items

@rounter.get("/my", response_model=List[ItemResponse])
async def get_my_items(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    items = db.query(Item).filter(Item.owner_id == current_user["id"], Item.deleted_at == None).offset(skip).limit(limit).all()
    return items

@rounter.get("/my/{item_id}/pricehistories", response_model=List[PriceHistoryResponse])
async def get_price_item_histories(
    item_id : int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    item_db = db.query(Item).filter(Item.id == item_id, Item.deleted_at == None).first()
    if not item_db:
        raise HTTPException(status_code=404, detail="Item not found")
    
    item_histories_db = db.query(PriceHistory).filter(
        PriceHistory.item_id == item_id, 
        PriceHistory.user_id == current_user["id"]
    ).offset(skip).limit(limit).all()

    return item_histories_db


# get item by id (detail page)
@rounter.get("/{item_id}", response_model=ItemResponse)
async def get_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

@rounter.post("/my", response_model=ItemResponse)
async def create_my_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    existing_item_this_user_db = db.query(Item).filter(Item.name == item.name ,Item.owner_id == current_user["id"]).first()
    if existing_item_this_user_db :
        raise HTTPException(status_code=403, detail="Item already exist in this user")
    
    db_item = Item(
        name=item.name,
        description=item.description,
        price=item.price,
        quantity=item.quantity,
        status=item.status.value,
        image_url=item.image_url,
        search_text=item.search_text,
        owner_id=current_user["id"],
        category_id=item.category_id,
        group_id= None
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    new_price_history_db = PriceHistory(
        price = item.price,
        item_id = db_item.id,
        user_id = current_user["id"],
    )

    db.add(new_price_history_db)
    db.commit()
    db.refresh(new_price_history_db)

    return db_item

@rounter.put("/my/{item_id}", response_model=ItemResponse)
async def update_my_item(
    item_id: int,
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user["id"]).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.name = item.name
    db_item.description = item.description
    db_item.price = item.price
    db_item.quantity = item.quantity
    db_item.status = item.status.value
    db_item.image_url = item.image_url
    db_item.search_text = item.search_text
    db_item.category_id = item.category_id
    db_item.group_id = db_item.group_id
    
    db.commit()
    db.refresh(db_item)
    return db_item

@rounter.delete("/my/{item_id}")
async def delete_my_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user["id"]).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.deleted_at = datetime.now(ZoneInfo("Asia/Bangkok"))
    db.commit()
    return {"detail": "Item deleted"}

@rounter.patch("/my/{item_id}/status", response_model=ItemResponse)
async def change_item_status(
    item_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    if status not in [s.value for s in ItemStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    db_item = db.query(Item).filter(Item.id == item_id, Item.owner_id == current_user["id"]).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.status = status
    db.commit()
    db.refresh(db_item)
    return db_item
