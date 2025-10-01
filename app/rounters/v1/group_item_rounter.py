
from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List, Optional
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...db.models.items.item import Item
from ...db.models.Groups.group import Group
from ..v1.group_rounter import rounter as group_rounter
from ...schemas.item_schema import ItemCreate, ItemResponse, ItemStatus
from ...core.security import get_current_user
from app.schemas.group_item_schema import GroupItemCreate, GroupItemResponse, GroupItemStatus
from app.db.models.Groups.group_item import GroupItem

rounter = APIRouter(prefix="/group_item", tags=["group_item"])


#ดึง item by group id + pagination (หน้า shop)
@rounter.get("/group/{group_id}/items", response_model=List[ItemResponse])
async def get_items_by_group(
    group_id: int,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    items = db.query(Item).join(GroupItem, Item.id == GroupItem.item_id)\
                           .filter(GroupItem.group_id == group_id).all()
    return items

# post item ใน group (ร้านของตัวเอง)
@rounter.post("/group/my/{group_id}/items/{item_id}", response_model=GroupItemResponse)
async def create_item_in_group(
    group_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    #check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    #จะเพิ่ม role check ในอนาคต เพราะอาจจะมีทั้ง owner และ admin ที่สามารถเพิ่ม item ได้
    db_group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user["id"]).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found or you're not the owner")
    
    exiting_item = db.query(GroupItem).filter(GroupItem.item_id == item_id, GroupItem.group_id == group_id).first()
    if exiting_item :
        raise HTTPException(status_code=403, detail="item already add to this group or item not found")
    
    new_group_item = GroupItem(
        group_id= group_id,
        item_id= item_id
    )

    db.add(new_group_item)
    db.commit()
    db.refresh(new_group_item)
    return new_group_item

#ลบ item ออกจาก group (ร้านของตัวเอง) by id
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
    db_item = db.query(GroupItem).filter(
        GroupItem.group_id == group_id, 
        GroupItem.item_id == item_id,
    ).first()

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(db_item)
    db.commit()

    return Response(status_code=204)
