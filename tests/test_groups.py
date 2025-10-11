"""
Unit tests for group endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.db.models.Groups.group import Group
from app.db.models.Groups.groupMember import GroupMember
from app.db.models.Users.User import User


@pytest.fixture
def test_group(db_session: Session, test_user: User) -> Group:
    """สร้าง test group"""
    group = Group(
        name="Test Group",
        description="Test group description",
        image_url="https://example.com/image.jpg",
        owner_id=test_user.id,
        follower_count=0,
    )
    db_session.add(group)
    db_session.commit()
    db_session.refresh(group)

    # สร้าง owner member
    owner_member = GroupMember(group_id=group.id, user_id=test_user.id, role="owner")
    db_session.add(owner_member)
    db_session.commit()

    return group


@pytest.fixture
def multiple_test_groups(db_session: Session, test_user: User) -> list[Group]:
    """สร้าง test groups หลายรายการ"""
    groups = []
    for i in range(1, 6):
        group = Group(
            name=f"Test Group {i}",
            description=f"Description for group {i}",
            image_url=f"https://example.com/image{i}.jpg",
            owner_id=test_user.id,
            follower_count=i * 10,
        )
        db_session.add(group)
        groups.append(group)

    db_session.commit()
    for group in groups:
        db_session.refresh(group)
        # สร้าง owner member
        owner_member = GroupMember(
            group_id=group.id, user_id=test_user.id, role="owner"
        )
        db_session.add(owner_member)

    db_session.commit()
    return groups


class TestGetMyGroups:
    """Test suite for GET /v1/group/my endpoint"""

    def test_get_my_groups_requires_authentication(self, client: TestClient):
        """
        Test: ดึง groups ของตัวเองโดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.get("/v1/group/my")
        assert response.status_code == 401

    def test_get_my_groups_empty(self, authenticated_client: TestClient):
        """
        Test: ดึง groups ของตัวเองเมื่อยังไม่มี groups
        Expected: ได้รับ list ว่าง
        """
        response = authenticated_client.get("/v1/group/my")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_my_groups_with_data(
        self, authenticated_client: TestClient, multiple_test_groups: list[Group]
    ):
        """
        Test: ดึง groups ของตัวเองทั้งหมด
        Expected: ได้รับ list ของ groups ที่เป็นเจ้าของ
        """
        response = authenticated_client.get("/v1/group/my")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all("id" in group for group in data)
        assert all("name" in group for group in data)
        assert all("owner_id" in group for group in data)

    def test_get_my_groups_excludes_deleted(
        self, authenticated_client: TestClient, test_group: Group, db_session: Session
    ):
        """
        Test: ดึง groups ต้องไม่แสดง groups ที่ถูกลบ
        Expected: ไม่มี groups ที่ถูกลบในผลลัพธ์
        """
        # ทำเครื่องหมาย group เป็นลบ
        test_group.deleted_at = datetime.utcnow()
        db_session.commit()

        response = authenticated_client.get("/v1/group/my")

        assert response.status_code == 200
        data = response.json()
        group_ids = [g["id"] for g in data]
        assert test_group.id not in group_ids


class TestCreateGroup:
    """Test suite for POST /v1/group/my endpoint"""

    def test_create_group_requires_authentication(self, client: TestClient):
        """
        Test: สร้าง group โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        group_data = {
            "name": "New Group",
            "description": "New group description",
            "image_url": "https://example.com/image.jpg",
            "owner_id": 1,
        }

        response = client.post("/v1/group/my", json=group_data)
        assert response.status_code == 401

    def test_create_group_success(
        self, authenticated_client: TestClient, test_user: User, db_session: Session
    ):
        """
        Test: สร้าง group ใหม่สำเร็จ
        Expected: ได้รับ group ที่สร้างพร้อม id และสร้าง owner member
        """
        group_data = {
            "name": "My New Group",
            "description": "This is my new group",
            "image_url": "https://example.com/new.jpg",
            "owner_id": test_user.id,
        }

        response = authenticated_client.post("/v1/group/my", json=group_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "My New Group"
        assert data["description"] == "This is my new group"
        assert data["owner_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data

        # Verify owner member was created
        group_id = data["id"]
        owner_member = (
            db_session.query(GroupMember)
            .filter(
                GroupMember.group_id == group_id,
                GroupMember.user_id == test_user.id,
                GroupMember.role == "owner",
            )
            .first()
        )
        assert owner_member is not None

    def test_create_group_duplicate_name(
        self, authenticated_client: TestClient, test_user: User, test_group: Group
    ):
        """
        Test: สร้าง group ด้วยชื่อที่มีอยู่แล้ว
        Expected: ได้รับ status 400
        """
        group_data = {
            "name": test_group.name,
            "description": "Different description",
            "image_url": "https://example.com/different.jpg",
            "owner_id": test_user.id,
        }

        response = authenticated_client.post("/v1/group/my", json=group_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_create_group_with_missing_required_fields(
        self, authenticated_client: TestClient
    ):
        """
        Test: สร้าง group โดยขาด required fields
        Expected: ได้รับ status 422 validation error
        """
        response = authenticated_client.post("/v1/group/my", json={})
        assert response.status_code == 422

    def test_create_group_without_description(
        self, authenticated_client: TestClient, test_user: User
    ):
        """
        Test: สร้าง group โดยไม่มี description (optional field)
        Expected: สร้างสำเร็จ
        """
        group_data = {"name": "Group Without Description", "owner_id": test_user.id}

        response = authenticated_client.post("/v1/group/my", json=group_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Group Without Description"


class TestUpdateGroup:
    """Test suite for PUT /v1/group/my/{group_id} endpoint"""

    def test_update_group_requires_authentication(
        self, client: TestClient, test_group: Group
    ):
        """
        Test: อัพเดท group โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        update_data = {
            "name": "Updated Name",
            "description": "Updated description",
            "owner_id": 1,
        }

        response = client.put(f"/v1/group/my/{test_group.id}", json=update_data)
        assert response.status_code == 401

    def test_update_group_success(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_user: User,
        db_session: Session,
    ):
        """
        Test: อัพเดท group ของตัวเองสำเร็จ
        Expected: ข้อมูล group ถูกอัพเดท
        """
        update_data = {
            "name": "Updated Group Name",
            "description": "Updated description",
            "image_url": "https://example.com/updated.jpg",
            "owner_id": test_user.id,
        }

        response = authenticated_client.put(
            f"/v1/group/my/{test_group.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Group Name"
        assert data["description"] == "Updated description"
        assert data["image_url"] == "https://example.com/updated.jpg"

        # Verify in database
        db_session.refresh(test_group)
        assert test_group.name == "Updated Group Name"

    def test_update_group_not_owner(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_user: User,
        db_session: Session,
    ):
        """
        Test: อัพเดท group ที่ไม่ใช่ของตัวเอง
        Expected: ได้รับ status 404
        """
        # สร้าง group ของ user อื่น
        import bcrypt

        another_user = User(
            username="anotheruser",
            full_name="Another User",
            email="another@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(another_user)
        db_session.commit()

        another_group = Group(
            name="Another Group",
            description="Not my group",
            owner_id=another_user.id,
            follower_count=0,
        )
        db_session.add(another_group)
        db_session.commit()
        db_session.refresh(another_group)

        update_data = {
            "name": "Trying to Update",
            "description": "Should fail",
            "owner_id": test_user.id,
        }

        response = authenticated_client.put(
            f"/v1/group/my/{another_group.id}", json=update_data
        )

        assert response.status_code == 404
        assert "not the owner" in response.json()["detail"]

    def test_update_group_not_found(
        self, authenticated_client: TestClient, test_user: User
    ):
        """
        Test: อัพเดท group ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        update_data = {
            "name": "Updated Name",
            "description": "Updated description",
            "owner_id": test_user.id,
        }

        response = authenticated_client.put("/v1/group/my/99999", json=update_data)

        assert response.status_code == 404


class TestDeleteGroup:
    """Test suite for DELETE /v1/group/my/{group_id} endpoint"""

    def test_delete_group_requires_authentication(
        self, client: TestClient, test_group: Group
    ):
        """
        Test: ลบ group โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.delete(f"/v1/group/my/{test_group.id}")
        assert response.status_code == 401

    def test_delete_group_success(
        self, authenticated_client: TestClient, test_group: Group, db_session: Session
    ):
        """
        Test: ลบ group ของตัวเองสำเร็จ (soft delete)
        Expected: group ถูก soft delete
        """
        group_id = test_group.id

        response = authenticated_client.delete(f"/v1/group/my/{group_id}")

        assert response.status_code == 204

        # Verify soft deleted
        db_session.refresh(test_group)
        assert test_group.deleted_at is not None

    def test_delete_group_not_owner(
        self, authenticated_client: TestClient, db_session: Session
    ):
        """
        Test: ลบ group ที่ไม่ใช่ของตัวเอง
        Expected: ได้รับ status 404
        """
        # สร้าง group ของ user อื่น
        import bcrypt

        another_user = User(
            username="anotheruser2",
            full_name="Another User 2",
            email="another2@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(another_user)
        db_session.commit()

        another_group = Group(
            name="Another Group 2",
            description="Not my group",
            owner_id=another_user.id,
            follower_count=0,
        )
        db_session.add(another_group)
        db_session.commit()
        db_session.refresh(another_group)

        response = authenticated_client.delete(f"/v1/group/my/{another_group.id}")

        assert response.status_code == 404
        assert "not the owner" in response.json()["detail"]

    def test_delete_group_not_found(self, authenticated_client: TestClient):
        """
        Test: ลบ group ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.delete("/v1/group/my/99999")
        assert response.status_code == 404

    def test_deleted_group_not_in_my_groups(
        self, authenticated_client: TestClient, test_group: Group
    ):
        """
        Test: group ที่ถูกลบแล้วต้องไม่ปรากฏใน GET /v1/group/my
        Expected: ไม่พบ group ที่ถูกลบ
        """
        # ลบ group
        authenticated_client.delete(f"/v1/group/my/{test_group.id}")

        # ดึง list groups
        response = authenticated_client.get("/v1/group/my")

        assert response.status_code == 200
        data = response.json()
        group_ids = [g["id"] for g in data]
        assert test_group.id not in group_ids


class TestGetGroupById:
    """Test suite for GET /v1/group/{group_id} endpoint"""

    def test_get_group_by_id_success(self, client: TestClient, test_group: Group):
        """
        Test: ดึงข้อมูล group ด้วย ID (public endpoint)
        Expected: ได้รับข้อมูล group
        """
        response = client.get(f"/v1/group/{test_group.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_group.id
        assert data["name"] == test_group.name
        assert data["description"] == test_group.description

    def test_get_group_by_id_not_found(self, client: TestClient):
        """
        Test: ดึงข้อมูล group ด้วย ID ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = client.get("/v1/group/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Group not found"

    def test_get_deleted_group_not_found(
        self, client: TestClient, test_group: Group, db_session: Session
    ):
        """
        Test: ดึงข้อมูล group ที่ถูก soft delete แล้ว
        Expected: ได้รับ status 404
        """
        # ทำเครื่องหมาย group เป็นลบ
        test_group.deleted_at = datetime.utcnow()
        db_session.commit()

        response = client.get(f"/v1/group/{test_group.id}")

        assert response.status_code == 404


class TestGetAllGroups:
    """Test suite for GET /v1/group/ endpoint"""

    def test_list_all_groups_empty(self, client: TestClient):
        """
        Test: ดึง list groups ทั้งหมดเมื่อยังไม่มีข้อมูล
        Expected: ได้รับ list ว่าง
        """
        response = client.get("/v1/group/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_all_groups_with_data(
        self, client: TestClient, multiple_test_groups: list[Group]
    ):
        """
        Test: ดึง list groups ทั้งหมด (public endpoint)
        Expected: ได้รับ list ของ groups
        """
        response = client.get("/v1/group/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all("id" in group for group in data)
        assert all("name" in group for group in data)

    def test_list_all_groups_with_pagination(
        self, client: TestClient, multiple_test_groups: list[Group]
    ):
        """
        Test: ใช้ pagination (skip และ limit)
        Expected: ได้รับ groups ตามจำนวนที่กำหนด
        """
        response = client.get("/v1/group/?skip=0&limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # ทดสอบหน้าถัดไป
        response2 = client.get("/v1/group/?skip=3&limit=3")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 2

    def test_list_all_groups_excludes_deleted(
        self, client: TestClient, test_group: Group, db_session: Session
    ):
        """
        Test: ดึง groups ต้องไม่แสดง groups ที่ถูกลบ
        Expected: ไม่มี groups ที่ถูกลบในผลลัพธ์
        """
        # ทำเครื่องหมาย group เป็นลบ
        test_group.deleted_at = datetime.utcnow()
        db_session.commit()

        response = client.get("/v1/group/")

        assert response.status_code == 200
        data = response.json()
        group_ids = [g["id"] for g in data]
        assert test_group.id not in group_ids

    def test_list_all_groups_default_pagination(
        self, client: TestClient, db_session: Session, test_user: User
    ):
        """
        Test: ทดสอบ default pagination limit
        Expected: จำกัดผลลัพธ์ตาม default limit (10)
        """
        # สร้าง 15 groups
        for i in range(15):
            group = Group(
                name=f"Group {i}",
                description=f"Description {i}",
                owner_id=test_user.id,
                follower_count=0,
            )
            db_session.add(group)
        db_session.commit()

        response = client.get("/v1/group/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 10  # Default limit
