
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...db.models.items.main import Item
from ...db.models.Groups.main import Group
from ..v1.group_rounter import rounter as group_rounter
from ...schemas.item_schema import ItemCreate, ItemResponse, ItemStatus
from ...core.security import get_current_user

rounter = APIRouter(prefix="/group_item", tags=["group_item"])


#ดึง item by group id + pagination (หน้า shop)
@rounter.get("/group/{group_id}/items", response_model=List[ItemResponse])
async def get_items_by_group(
    group_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    items = db.query(Item).filter(Item.group_id == group_id).offset(skip).limit(limit).all()
    return items

# post item ใน group (ร้านของตัวเอง)
@rounter.post("/group/my/{group_id}/items", response_model=ItemResponse)
async def create_item_in_group(
    group_id: int,
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    #check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    #จะเพิ่ม role check ในอนาคต เพราะอาจจะมีทั้ง owner และ admin ที่สามารถเพิ่ม item ได้
    db_group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user["id"]).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found or you're not the owner")
    
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
        group_id=group_id
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


#แก้ไข item ใน group (ร้านของตัวเอง) by id
@rounter.put("/group/my/{group_id}/items/{item_id}", response_model=ItemResponse)
async def update_item_in_group(
    group_id: int,
    item_id: int,
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    #check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    db_group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user["id"]).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found or you're not the owner")
    
    #check ว่า item นี้อยู่ใน group ที่แก้ไขไหม
    db_item = db.query(Item).filter(Item.id == item_id, Item.group_id == group_id, Item.owner_id == current_user["id"]).first()
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
    
    db.commit()
    db.refresh(db_item)
    return db_item


#ลบ item ใน group (ร้านของตัวเอง) by id
@rounter.delete("/group/my/{group_id}/items/{item_id}")
async def delete_item_in_group(
    group_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    #check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    db_group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user["id"]).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found or you're not the owner")
    
    #check ว่า item นี้อยู่ใน group ที่แก้ไขไหม
    db_item = db.query(Item).filter(Item.id == item_id, Item.group_id == group_id, Item.owner_id == current_user["id"]).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    

    db_item.deleted_at = datetime.now(ZoneInfo("Asia/Bangkok"))
    db.commit()
    return {"detail": "Item deleted"}


#เปลี่ยนสถานะ item ใน group (ร้านของตัวเอง) by id
@rounter.patch("/group/{group_id}/items/{item_id}/status", response_model=ItemResponse)
async def change_item_status_in_group(
    group_id: int,
    item_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    
    #check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    db_group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user["id"]).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found or you're not the owner")
    #check ว่า status ที่ส่งมาถูกต้องไหม
    if status not in [s.value for s in ItemStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")
    #check ว่า item นี้อยู่ใน group ที่แก้ไขไหม
    db_item = db.query(Item).filter(Item.id == item_id, Item.group_id == group_id, Item.owner_id == current_user["id"]).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db_item.status = status
    db.commit()
    db.refresh(db_item)
    return db_item