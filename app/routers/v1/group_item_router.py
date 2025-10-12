from fastapi import APIRouter, Depends, HTTPException, Response
from typing import List
from sqlalchemy.orm import Session

from app.db.models.Groups.groupMember import GroupMember
from ...db.database import get_db
from ...db.models.items.item import Item
from ...db.models.Groups.group import Group
from ...schemas.item_schema import ItemResponse
from ...core.security import get_current_user

router = APIRouter(prefix="/group_item", tags=["group_item"])


# ดึง item by group id + pagination (หน้า shop)
@router.get("/group/{group_id}/items", response_model=List[ItemResponse])
async def get_items_by_group(
    group_id: int, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    items = (
        db.query(Item)
        .filter(
            Item.group_id == group_id,
            Item.deleted_at.is_(None),
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

    return items


# post item ใน group (ร้านของตัวเอง)
@router.post("/group/my/{group_id}/items/{item_id}", response_model=ItemResponse)
async def create_item_in_group(
    group_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    # จะเพิ่ม role check ในอนาคต เพราะอาจจะมีทั้ง owner และ admin ที่สามารถเพิ่ม item ได้

    user_id = current_user["id"]
    group_member = (
        db.query(GroupMember)
        .filter(GroupMember.user_id == user_id, GroupMember.group_id == group_id)
        .first()
    )

    if not group_member:
        raise HTTPException(
            status_code=403, detail="You are not a member of this group"
        )

    if group_member.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to add item to this group",
        )

    existing_item = (
        db.query(Item).filter(Item.id == item_id, Item.group_id == group_id).first()
    )
    if existing_item:
        raise HTTPException(
            status_code=403, detail="item already add to this group or item not found"
        )

    item_db = db.query(Item).filter(Item.id == item_id, Item.deleted_at.is_(None)).first()

    if not item_db:
        raise HTTPException(status_code=404, detail="item not found")

    item_db.group_id = group_id

    db.commit()
    db.refresh(item_db)
    return item_db


# ลบ item ออกจาก group (ร้านของตัวเอง) by id
@router.delete("/group/my/{group_id}/items/{item_id}")
async def delete_item_in_group(
    group_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):

    # check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    user_role = (
        db.query(Group)
        .join(GroupMember, Group.id == GroupMember.group_id)
        .filter(
            Group.id == group_id,
            GroupMember.user_id == current_user["id"],  # ต้องเป็น member ของ group
            GroupMember.role.in_(["owner", "admin"]),
        )
        .first()
    )

    if not user_role:
        raise HTTPException(
            status_code=404, detail="Group not found or you're not the owner"
        )

    # check ว่า item นี้อยู่ใน group ที่แก้ไขไหม

    db_item = (
        db.query(Item)
        .filter(
            Item.group_id == group_id,
            Item.id == item_id,
        )
        .first()
    )

    if not db_item:
        raise HTTPException(status_code=404, detail="Item not found")

    db_item.group_id = None
    db.commit()
    db.refresh(db_item)

    return Response(status_code=204)
