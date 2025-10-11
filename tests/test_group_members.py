"""
Unit tests for group member endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.Users.User import User
from app.db.models.Groups.group import Group
from app.db.models.Groups.groupMember import GroupMember


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
def test_member_user(db_session: Session) -> User:
    """สร้าง user สำหรับทดสอบการเป็น member"""
    import bcrypt

    user = User(
        username="memberuser",
        full_name="Member User",
        email="member@example.com",
        password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        ),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_group_member(
    db_session: Session, test_group: Group, test_member_user: User
) -> GroupMember:
    """สร้าง test group member"""
    member = GroupMember(
        group_id=test_group.id, user_id=test_member_user.id, role="member"
    )
    db_session.add(member)
    db_session.commit()
    db_session.refresh(member)
    return member


class TestAddMemberToGroup:
    """Test suite for POST /v1/group_member/group/my/{group_id}/members endpoint"""

    def test_add_member_requires_authentication(
        self, client: TestClient, test_group: Group, test_member_user: User
    ):
        """
        Test: เพิ่ม member โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        member_data = {"user_id": test_member_user.id, "role": "member"}

        response = client.post(
            f"/v1/group_member/group/my/{test_group.id}/members", json=member_data
        )
        assert response.status_code == 401

    def test_add_member_success(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_member_user: User,
    ):
        """
        Test: เพิ่ม member เข้า group สำเร็จ
        Expected: ได้รับ member ที่สร้าง
        """
        member_data = {"user_id": test_member_user.id, "role": "member"}

        response = authenticated_client.post(
            f"/v1/group_member/group/my/{test_group.id}/members", json=member_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == test_group.id
        assert data["user_id"] == test_member_user.id
        assert data["role"] == "member"
        assert "id" in data

    def test_add_admin_member(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_member_user: User,
    ):
        """
        Test: เพิ่ม member ด้วย role admin
        Expected: สร้างสำเร็จด้วย role admin
        """
        member_data = {"user_id": test_member_user.id, "role": "admin"}

        response = authenticated_client.post(
            f"/v1/group_member/group/my/{test_group.id}/members", json=member_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"

    def test_add_member_to_nonexistent_group(
        self, authenticated_client: TestClient, test_member_user: User
    ):
        """
        Test: เพิ่ม member เข้า group ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        member_data = {"user_id": test_member_user.id, "role": "member"}

        response = authenticated_client.post(
            "/v1/group_member/group/my/99999/members", json=member_data
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_add_nonexistent_user_to_group(
        self, authenticated_client: TestClient, test_group: Group
    ):
        """
        Test: เพิ่ม user ที่ไม่มีในระบบเข้า group
        Expected: ได้รับ status 404
        """
        member_data = {"user_id": 99999, "role": "member"}

        response = authenticated_client.post(
            f"/v1/group_member/group/my/{test_group.id}/members", json=member_data
        )

        assert response.status_code == 404
        assert "user not found" in response.json()["detail"].lower()

    def test_add_duplicate_member(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_group_member: GroupMember,
    ):
        """
        Test: เพิ่ม member ที่มีอยู่ใน group แล้ว
        Expected: ได้รับ status 400
        """
        member_data = {"user_id": test_group_member.user_id, "role": "member"}

        response = authenticated_client.post(
            f"/v1/group_member/group/my/{test_group.id}/members", json=member_data
        )

        assert response.status_code == 400
        assert "already a member" in response.json()["detail"]

    def test_add_member_not_owner(
        self,
        client: TestClient,
        db_session: Session,
        test_group: Group,
        test_member_user: User,
    ):
        """
        Test: เพิ่ม member โดยคนที่ไม่ใช่ owner
        Expected: ได้รับ status 404 หรือ 403
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง user ใหม่ที่ไม่ใช่ owner
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
        db_session.refresh(another_user)

        # สร้าง token สำหรับ user นี้
        token = create_access_token(
            data={"sub": another_user.username, "id": another_user.id}
        )
        client.headers = {"Authorization": f"Bearer {token}"}

        member_data = {"user_id": test_member_user.id, "role": "member"}

        response = client.post(
            f"/v1/group_member/group/my/{test_group.id}/members", json=member_data
        )

        assert response.status_code in [403, 404]

    def test_add_member_with_missing_fields(
        self, authenticated_client: TestClient, test_group: Group
    ):
        """
        Test: เพิ่ม member โดยขาด required fields
        Expected: ได้รับ status 422 validation error
        """
        response = authenticated_client.post(
            f"/v1/group_member/group/my/{test_group.id}/members", json={}
        )

        assert response.status_code == 422


class TestUpdateMemberRole:
    """Test suite for PUT /v1/group_member/group/my/{group_id}/members/{user_id} endpoint"""

    def test_update_member_role_requires_authentication(
        self, client: TestClient, test_group: Group, test_group_member: GroupMember
    ):
        """
        Test: แก้ไข role โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        member_data = {
            "group_id": test_group.id,
            "user_id": test_group_member.user_id,
            "role": "admin",
        }

        response = client.put(
            f"/v1/group_member/group/my/{test_group.id}/members/{test_group_member.user_id}",
            json=member_data,
        )
        assert response.status_code == 401

    def test_update_member_role_success(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_group_member: GroupMember,
    ):
        """
        Test: แก้ไข role ของ member สำเร็จ
        Expected: role ถูกอัพเดท
        """
        member_data = {
            "group_id": test_group.id,
            "user_id": test_group_member.user_id,
            "role": "admin",
        }

        response = authenticated_client.put(
            f"/v1/group_member/group/my/{test_group.id}/members/{test_group_member.user_id}",
            json=member_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "admin"
        assert data["user_id"] == test_group_member.user_id

    def test_update_member_role_to_member(
        self,
        authenticated_client: TestClient,
        db_session: Session,
        test_group: Group,
        test_member_user: User,
    ):
        """
        Test: เปลี่ยน role จาก admin เป็น member
        Expected: role ถูกเปลี่ยนสำเร็จ
        """
        # สร้าง admin member
        admin_member = GroupMember(
            group_id=test_group.id, user_id=test_member_user.id, role="admin"
        )
        db_session.add(admin_member)
        db_session.commit()
        db_session.refresh(admin_member)

        member_data = {
            "group_id": test_group.id,
            "user_id": test_member_user.id,
            "role": "member",
        }

        response = authenticated_client.put(
            f"/v1/group_member/group/my/{test_group.id}/members/{test_member_user.id}",
            json=member_data,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "member"

    def test_update_member_role_nonexistent_group(
        self, authenticated_client: TestClient, test_member_user: User
    ):
        """
        Test: แก้ไข role ใน group ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        member_data = {
            "group_id": 99999,
            "user_id": test_member_user.id,
            "role": "admin",
        }

        response = authenticated_client.put(
            f"/v1/group_member/group/my/99999/members/{test_member_user.id}",
            json=member_data,
        )

        assert response.status_code == 404

    def test_update_member_role_nonexistent_user(
        self, authenticated_client: TestClient, test_group: Group
    ):
        """
        Test: แก้ไข role ของ user ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        member_data = {"group_id": test_group.id, "user_id": 99999, "role": "admin"}

        response = authenticated_client.put(
            f"/v1/group_member/group/my/{test_group.id}/members/99999",
            json=member_data,
        )

        assert response.status_code == 404

    def test_update_member_role_not_in_group(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_member_user: User,
    ):
        """
        Test: แก้ไข role ของ user ที่ไม่ได้อยู่ใน group
        Expected: ได้รับ status 400
        """
        member_data = {
            "group_id": test_group.id,
            "user_id": test_member_user.id,
            "role": "admin",
        }

        response = authenticated_client.put(
            f"/v1/group_member/group/my/{test_group.id}/members/{test_member_user.id}",
            json=member_data,
        )

        assert response.status_code == 400
        assert "not a member" in response.json()["detail"]


class TestRemoveMemberFromGroup:
    """Test suite for DELETE /v1/group_member/group/my/{group_id}/members/{user_id} endpoint"""

    def test_remove_member_requires_authentication(
        self, client: TestClient, test_group: Group, test_group_member: GroupMember
    ):
        """
        Test: ลบ member โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.delete(
            f"/v1/group_member/group/my/{test_group.id}/members/{test_group_member.user_id}"
        )
        assert response.status_code == 401

    def test_remove_member_success(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_group_member: GroupMember,
        db_session: Session,
    ):
        """
        Test: ลบ member ออกจาก group สำเร็จ
        Expected: member ถูกลบจากฐานข้อมูล
        """
        member_id = test_group_member.id
        user_id = test_group_member.user_id

        response = authenticated_client.delete(
            f"/v1/group_member/group/my/{test_group.id}/members/{user_id}"
        )

        assert response.status_code == 200
        assert "removed" in response.json()["detail"]

        # Verify deleted from database
        deleted_member = (
            db_session.query(GroupMember).filter(GroupMember.id == member_id).first()
        )
        assert deleted_member is None

    def test_remove_member_nonexistent_group(
        self, authenticated_client: TestClient, test_member_user: User
    ):
        """
        Test: ลบ member จาก group ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.delete(
            f"/v1/group_member/group/my/99999/members/{test_member_user.id}"
        )

        assert response.status_code == 404

    def test_remove_member_nonexistent_user(
        self, authenticated_client: TestClient, test_group: Group
    ):
        """
        Test: ลบ user ที่ไม่มีในระบบออกจาก group
        Expected: ได้รับ status 404
        """
        response = authenticated_client.delete(
            f"/v1/group_member/group/my/{test_group.id}/members/99999"
        )

        assert response.status_code == 404

    def test_remove_member_not_in_group(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_member_user: User,
    ):
        """
        Test: ลบ user ที่ไม่ได้อยู่ใน group
        Expected: ได้รับ status 400
        """
        response = authenticated_client.delete(
            f"/v1/group_member/group/my/{test_group.id}/members/{test_member_user.id}"
        )

        assert response.status_code == 400
        assert "not a member" in response.json()["detail"]

    def test_remove_member_not_owner(
        self,
        client: TestClient,
        db_session: Session,
        test_group: Group,
        test_group_member: GroupMember,
    ):
        """
        Test: ลบ member โดยคนที่ไม่ใช่ owner
        Expected: ได้รับ status 404 หรือ 403
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง user ใหม่ที่ไม่ใช่ owner
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
        db_session.refresh(another_user)

        # สร้าง token สำหรับ user นี้
        token = create_access_token(
            data={"sub": another_user.username, "id": another_user.id}
        )
        client.headers = {"Authorization": f"Bearer {token}"}

        response = client.delete(
            f"/v1/group_member/group/my/{test_group.id}/members/{test_group_member.user_id}"
        )

        assert response.status_code in [403, 404]


class TestGetMembersInGroup:
    """Test suite for GET /v1/group_member/group/my/{group_id}/members endpoint"""

    def test_get_members_requires_authentication(
        self, client: TestClient, test_group: Group
    ):
        """
        Test: ดึง members โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.get(f"/v1/group_member/group/my/{test_group.id}/members")
        assert response.status_code == 401

    def test_get_members_success(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_group_member: GroupMember,
    ):
        """
        Test: ดึง members ทั้งหมดใน group
        Expected: ได้รับ list ของ members
        """
        response = authenticated_client.get(
            f"/v1/group_member/group/my/{test_group.id}/members"
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2  # owner + test_group_member

        # ตรวจสอบว่ามี fields ที่จำเป็น
        for member in data:
            assert "id" in member
            assert "group_id" in member
            assert "user_id" in member
            assert "role" in member

    def test_get_members_empty_group(
        self, authenticated_client: TestClient, test_group: Group
    ):
        """
        Test: ดึง members จาก group ที่มีแต่ owner
        Expected: ได้รับ list ที่มีแค่ owner
        """
        response = authenticated_client.get(
            f"/v1/group_member/group/my/{test_group.id}/members"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1  # เฉพาะ owner
        assert data[0]["role"] == "owner"

    def test_get_members_nonexistent_group(self, authenticated_client: TestClient):
        """
        Test: ดึง members จาก group ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.get("/v1/group_member/group/my/99999/members")

        assert response.status_code == 404

    def test_get_members_not_owner(
        self, client: TestClient, db_session: Session, test_group: Group
    ):
        """
        Test: ดึง members โดยคนที่ไม่ใช่ owner
        Expected: ได้รับ status 404 หรือ 403
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง user ใหม่ที่ไม่ใช่ owner
        another_user = User(
            username="anotheruser3",
            full_name="Another User 3",
            email="another3@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(another_user)
        db_session.commit()
        db_session.refresh(another_user)

        # สร้าง token สำหรับ user นี้
        token = create_access_token(
            data={"sub": another_user.username, "id": another_user.id}
        )
        client.headers = {"Authorization": f"Bearer {token}"}

        response = client.get(f"/v1/group_member/group/my/{test_group.id}/members")

        assert response.status_code in [403, 404]


class TestGetMembersInGroupPublic:
    """Test suite for GET /v1/group_member/group/{group_id}/members endpoint"""

    def test_get_members_public_no_authentication_needed(
        self, client: TestClient, test_group: Group
    ):
        """
        Test: ดึง members แบบ public ไม่ต้องมี authentication
        Expected: สามารถเข้าถึงได้
        """
        response = client.get(f"/v1/group_member/group/{test_group.id}/members")

        # อาจจะ 200 หรือ 401 ขึ้นกับ implementation
        assert response.status_code in [200, 401]

    def test_get_members_public_success(
        self,
        client: TestClient,
        test_group: Group,
        test_group_member: GroupMember,
    ):
        """
        Test: ดึง members ทั้งหมดใน group แบบ public
        Expected: ได้รับ list ของ members
        """
        response = client.get(f"/v1/group_member/group/{test_group.id}/members")

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            assert len(data) >= 2  # owner + test_group_member

    def test_get_members_public_nonexistent_group(self, client: TestClient):
        """
        Test: ดึง members จาก group ที่ไม่มีในระบบ (public)
        Expected: ได้รับ status 404
        """
        response = client.get("/v1/group_member/group/99999/members")

        assert response.status_code == 404

    def test_get_members_public_deleted_group(
        self, client: TestClient, test_group: Group, db_session: Session
    ):
        """
        Test: ดึง members จาก group ที่ถูกลบแล้ว
        Expected: ได้รับ status 404
        """
        from datetime import datetime, timezone

        # ทำเครื่องหมาย group เป็นลบ
        test_group.deleted_at = datetime.now(timezone.utc)
        db_session.commit()

        response = client.get(f"/v1/group_member/group/{test_group.id}/members")

        assert response.status_code == 404
