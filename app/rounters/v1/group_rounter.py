from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional

from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from ...db.database import get_db

from ...db.models.Groups.group import Group
from app.schemas.group_schema import GroupCreate, GroupResponse

from app.core.security import get_current_user

from app.rounters.v1.group_member_rounter import add_member_to_group
from app.db.models.Groups.groupMember import GroupMember

rounter = APIRouter(prefix="/group", tags=["group"])

#1. ดึง group ของตัวเอง (ร้านของตัวเอง) + pagination
@rounter.get("/my", response_model=List[GroupResponse])
async def get_my_groups(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    groups = db.query(Group).filter(Group.owner_id == current_user["id"], Group.deleted_at == None).all()
    return groups

#2. สร้าง group (ร้านของตัวเอง)
@rounter.post("/my", response_model=GroupResponse)
async def create_group(group: GroupCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    existing_group = db.query(Group).filter(Group.name == group.name).first()
    if existing_group:
        raise HTTPException(
            status_code=400,
            detail=f"Group name '{group.name}' already exists"
        )
    
    new_group = Group(
        name=group.name,
        description=group.description,
        image_url=group.image_url,
        owner_id=current_user["id"],

        follower_count=0,
        created_at=datetime.now(ZoneInfo("Asia/Bangkok")),
        updated_at=datetime.now(ZoneInfo("Asia/Bangkok"))
    )
    db.add(new_group)
    db.commit()
    db.refresh(new_group)

    owner_member = GroupMember(
        group_id=new_group.id,
        user_id=current_user["id"],
        role="owner"
    )

    db.add(owner_member)
    db.commit()
    db.refresh(owner_member)

    return new_group

#3. แก้ไข group (ร้านของตัวเอง) by id
@rounter.put("/my/{group_id}", response_model=GroupResponse)
async def update_group(group_id: int, group: GroupCreate, db: Session = Depends (get_db), current_user: dict = Depends(get_current_user)):
    db_group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user["id"]).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found or you're not the owner")
    
    db_group.name = group.name
    db_group.description = group.description
    db_group.image_url = group.image_url
    db_group.updated_at = datetime.now(ZoneInfo("Asia/Bangkok"))
    
    db.commit()
    db.refresh(db_group)
    return db_group

#4. ลบ group (ร้านของตัวเอง) by id
@rounter.delete("/my/{group_id}")
async def delete_group(group_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    db_group = db.query(Group).filter(Group.id == group_id, Group.owner_id == current_user["id"]).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found or you're not the owner")
    
    db_group.deleted_at = datetime.now(ZoneInfo("Asia/Bangkok"))
    db.commit()
    return {"detail": "Group deleted"}

#5. ดึง group by id (สาธารณะ)
@rounter.get("/{group_id}", response_model=GroupResponse)
async def get_group_by_id(group_id: int, db: Session = Depends(get_db)):
    db_group = db.query(Group).filter(Group.id == group_id, Group.deleted_at == None).first()
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")
    return db_group

#6. ดึง group ทั้งหมด (สาธารณะ) + pagination
#เดี๋ยวคิดว่าจะเพิ่ม query string เพื่อเป็น logic ในการค้นหากลุ่ม เช่น กลุ่มที่มี follower มากที่สุด, กลุ่มที่มี item มากที่สุด, กลุ่มที่มี item ลดราคามากที่สุด
@rounter.get("/", response_model=List[GroupResponse])
async def get_all_groups(skip: int = 0, limit: int = 10,    db: Session = Depends(get_db)):
    groups = db.query(Group).filter(Group.deleted_at == None).offset(skip).limit(limit).all()
    return groups