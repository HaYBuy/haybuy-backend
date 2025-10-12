from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.orm import Session
from ...db.database import get_db
from ...db.models.Groups.group import Group
from ...db.models.Groups.groupMember import GroupMember
from ...db.models.Users.User import User
from ...schemas.group_member_schema import (
    GroupMemberCreate,
    GroupMemberAdd,
    GroupMemberResponse,
    GroupMemberRole,
)
from ...core.security import get_current_user

router = APIRouter(prefix="/group_member", tags=["group_member"])

# Constants
GROUP_NOT_FOUND_OR_NOT_OWNER = "Group not found or you're not the owner"


# เพิ่ม member เข้า group (ร้านของตัวเอง) by group_id
@router.post("/group/my/{group_id}/members", response_model=GroupMemberResponse)
async def add_member_to_group(
    group_id: int,
    member: GroupMemberAdd,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    db_group = (
        db.query(Group)
        .filter(Group.id == group_id, Group.owner_id == current_user["id"])
        .first()
    )
    if not db_group:
        raise HTTPException(status_code=404, detail=GROUP_NOT_FOUND_OR_NOT_OWNER)

    # check ว่า user ที่จะเพิ่มเข้า group มีอยู่จริงไหม
    db_user = db.query(User).filter(User.id == member.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # check ว่า user คนนี้อยู่ใน group นี้แล้วหรือยัง
    existing_member = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == member.user_id)
        .first()
    )
    if existing_member:
        raise HTTPException(
            status_code=400, detail="User is already a member of this group"
        )

    new_member = GroupMember(
        group_id=group_id,
        user_id=member.user_id,
        role=member.role,
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    return new_member


# แก้ไข role member ใน group (ร้านของตัวเอง) by group_id และ user_id
@router.put(
    "/group/my/{group_id}/members/{user_id}", response_model=GroupMemberResponse
)
async def update_member_role_in_group(
    member: GroupMemberCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    db_group = (
        db.query(Group)
        .filter(Group.id == member.group_id, Group.owner_id == current_user["id"])
        .first()
    )
    if not db_group:
        raise HTTPException(status_code=404, detail=GROUP_NOT_FOUND_OR_NOT_OWNER)

    # check ว่า user ที่จะเพิ่มเข้า group มีอยู่จริงไหม
    db_user = db.query(User).filter(User.id == member.user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # check ว่า user คนนี้อยู่ใน group นี้หรือยัง
    existing_member = (
        db.query(GroupMember)
        .filter(
            GroupMember.group_id == member.group_id,
            GroupMember.user_id == member.user_id,
        )
        .first()
    )
    if not existing_member:
        raise HTTPException(
            status_code=400, detail="User is not a member of this group"
        )

    if member.role not in GroupMemberRole:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {member.role}",
        )

    existing_member.role = member.role
    db.commit()
    db.refresh(existing_member)
    return existing_member


# ลบ member ออกจาก group (ร้านของตัวเอง) by group_id และ user_id
@router.delete("/group/my/{group_id}/members/{user_id}")
async def remove_member_from_group(
    group_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    db_group = (
        db.query(Group)
        .filter(Group.id == group_id, Group.owner_id == current_user["id"])
        .first()
    )
    if not db_group:
        raise HTTPException(status_code=404, detail=GROUP_NOT_FOUND_OR_NOT_OWNER)

    # check ว่า user ที่จะลบออกจาก group มีอยู่จริงไหม
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    # check ว่า user คนนี้อยู่ใน group นี้หรือยัง
    existing_member = (
        db.query(GroupMember)
        .filter(GroupMember.group_id == group_id, GroupMember.user_id == user_id)
        .first()
    )
    if not existing_member:
        raise HTTPException(
            status_code=400, detail="User is not a member of this group"
        )

    db.delete(existing_member)
    db.commit()
    return {"detail": "Member removed from group"}


# ดึง member ทั้งหมดใน group (ร้านของตัวเอง) by group_id
@router.get("/group/my/{group_id}/members", response_model=List[GroupMemberResponse])
async def get_members_in_group(
    group_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    # check ว่ามี group_id นี้อยู่จริงไหม และมีสิทธิ์เป็นแก้ไข group นี้ไหม
    db_group = (
        db.query(Group)
        .filter(Group.id == group_id, Group.owner_id == current_user["id"])
        .first()
    )
    if not db_group:
        raise HTTPException(status_code=404, detail=GROUP_NOT_FOUND_OR_NOT_OWNER)

    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    return members


# ดึง member ทั้งหมดใน group (ร้านของตัวเอง) by group_id
@router.get("/group/{group_id}/members", response_model=List[GroupMemberResponse])
async def get_members_in_group_public(group_id: int, db: Session = Depends(get_db)):
    # check ว่ามี group_id นี้อยู่จริงไหม
    db_group = (
        db.query(Group)
        .filter(
            Group.id == group_id, Group.deleted_at == None
        )  # noqa: E711 - SQLAlchemy requires == None
        .first()
    )
    if not db_group:
        raise HTTPException(status_code=404, detail="Group not found")

    members = db.query(GroupMember).filter(GroupMember.group_id == group_id).all()
    return members
