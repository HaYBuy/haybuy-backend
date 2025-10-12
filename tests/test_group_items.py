"""
Unit tests for group item endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.models.Users.User import User
from app.db.models.Groups.group import Group
from app.db.models.Groups.groupMember import GroupMember
from app.db.models.items.item import Item
from app.db.models.Categorys.main import Category


@pytest.fixture
def test_category(db_session: Session) -> Category:
    """สร้าง test category"""
    category = Category(name="Electronics", slug="electronics", parent_id=None)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


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
def test_item(db_session: Session, test_user: User, test_category: Category) -> Item:
    """สร้าง test item (ไม่มี group_id)"""
    item = Item(
        name="Test Item",
        description="Test item description",
        price=Decimal("99.99"),
        quantity=10,
        status="available",
        owner_id=test_user.id,
        category_id=test_category.id,
        group_id=None,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_group_item(
    db_session: Session, test_user: User, test_category: Category, test_group: Group
) -> Item:
    """สร้าง item ที่อยู่ใน group แล้ว"""
    item = Item(
        name="Group Item",
        description="Item in group",
        price=Decimal("49.99"),
        quantity=5,
        status="available",
        owner_id=test_user.id,
        category_id=test_category.id,
        group_id=test_group.id,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def multiple_test_group_items(
    db_session: Session, test_user: User, test_category: Category, test_group: Group
) -> list[Item]:
    """สร้าง test items หลายรายการใน group"""
    items = []
    for i in range(1, 6):
        item = Item(
            name=f"Group Item {i}",
            description=f"Description for item {i}",
            price=Decimal(f"{i * 10}.99"),
            quantity=i * 5,
            status="available",
            owner_id=test_user.id,
            category_id=test_category.id,
            group_id=test_group.id,
        )
        db_session.add(item)
        items.append(item)

    db_session.commit()
    for item in items:
        db_session.refresh(item)

    return items


class TestGetItemsByGroup:
    """Test suite for GET /v1/group_item/group/{group_id}/items endpoint"""

    def test_get_items_by_group_empty(self, client: TestClient, test_group: Group):
        """
        Test: ดึง items จาก group ที่ยังไม่มี items
        Expected: ได้รับ list ว่าง
        """
        response = client.get(f"/v1/group_item/group/{test_group.id}/items")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_items_by_group_with_data(
        self,
        client: TestClient,
        test_group: Group,
        multiple_test_group_items: list[Item],
    ):
        """
        Test: ดึง items ทั้งหมดใน group
        Expected: ได้รับ list ของ items
        """
        response = client.get(f"/v1/group_item/group/{test_group.id}/items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all("id" in item for item in data)
        assert all("name" in item for item in data)
        assert all(item["group_id"] == test_group.id for item in data)

    def test_get_items_by_group_with_pagination(
        self,
        client: TestClient,
        test_group: Group,
        multiple_test_group_items: list[Item],
    ):
        """
        Test: ใช้ pagination (skip และ limit)
        Expected: ได้รับ items ตามจำนวนที่กำหนด
        """
        response = client.get(
            f"/v1/group_item/group/{test_group.id}/items?skip=0&limit=3"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # ทดสอบหน้าถัดไป
        response2 = client.get(
            f"/v1/group_item/group/{test_group.id}/items?skip=3&limit=3"
        )
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 2  # เหลืออีก 2 items

    def test_get_items_by_nonexistent_group(self, client: TestClient):
        """
        Test: ดึง items จาก group ที่ไม่มีในระบบ
        Expected: ได้รับ list ว่าง (ไม่มี items ในกรณีนี้)
        """
        response = client.get("/v1/group_item/group/99999/items")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_items_excludes_deleted_items(
        self,
        client: TestClient,
        test_group: Group,
        test_group_item: Item,
        db_session: Session,
    ):
        """
        Test: ดึง items ต้องไม่แสดง items ที่ถูกลบ
        Expected: ไม่มี items ที่ถูกลบในผลลัพธ์
        """
        from datetime import datetime, timezone

        # ทำเครื่องหมาย item เป็นลบ
        test_group_item.deleted_at = datetime.now(timezone.utc)
        db_session.commit()

        response = client.get(f"/v1/group_item/group/{test_group.id}/items")

        assert response.status_code == 200
        data = response.json()
        item_ids = [item["id"] for item in data]
        assert test_group_item.id not in item_ids

    def test_get_items_no_authentication_needed(
        self, client: TestClient, test_group: Group, test_group_item: Item
    ):
        """
        Test: ดึง items ใน group ไม่ต้องมี authentication (public)
        Expected: สามารถเข้าถึงได้
        """
        response = client.get(f"/v1/group_item/group/{test_group.id}/items")

        assert response.status_code == 200


class TestAddItemToGroup:
    """Test suite for POST /v1/group_item/group/my/{group_id}/items/{item_id} endpoint"""

    def test_add_item_to_group_requires_authentication(
        self, client: TestClient, test_group: Group, test_item: Item
    ):
        """
        Test: เพิ่ม item เข้า group โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.post(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_item.id}"
        )
        assert response.status_code == 401

    def test_add_item_to_group_success(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_item: Item,
        db_session: Session,
    ):
        """
        Test: เพิ่ม item เข้า group สำเร็จ
        Expected: item ถูกเพิ่มเข้า group (group_id ถูกอัพเดท)
        """
        response = authenticated_client.post(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_item.id}"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_item.id
        assert data["group_id"] == test_group.id

        # Verify in database
        db_session.refresh(test_item)
        assert test_item.group_id == test_group.id

    def test_add_item_to_group_by_admin(
        self,
        client: TestClient,
        db_session: Session,
        test_group: Group,
        test_item: Item,
    ):
        """
        Test: เพิ่ม item เข้า group โดย admin member
        Expected: สามารถเพิ่มได้สำเร็จ
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง admin user
        admin_user = User(
            username="adminuser",
            full_name="Admin User",
            email="admin@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)

        # เพิ่มเป็น admin member
        admin_member = GroupMember(
            group_id=test_group.id, user_id=admin_user.id, role="admin"
        )
        db_session.add(admin_member)
        db_session.commit()

        # สร้าง item ของ admin
        admin_item = Item(
            name="Admin Item",
            description="Item by admin",
            price=Decimal("29.99"),
            quantity=3,
            status="available",
            owner_id=admin_user.id,
            category_id=test_item.category_id,
            group_id=None,
        )
        db_session.add(admin_item)
        db_session.commit()
        db_session.refresh(admin_item)

        # สร้าง token สำหรับ admin
        token = create_access_token(
            data={"sub": admin_user.username, "id": admin_user.id}
        )
        client.headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            f"/v1/group_item/group/my/{test_group.id}/items/{admin_item.id}"
        )

        assert response.status_code == 200

    def test_add_item_to_group_nonexistent_group(
        self, authenticated_client: TestClient, test_item: Item
    ):
        """
        Test: เพิ่ม item เข้า group ที่ไม่มีในระบบ
        Expected: ได้รับ status 403 หรือ 404
        """
        response = authenticated_client.post(
            f"/v1/group_item/group/my/99999/items/{test_item.id}"
        )

        assert response.status_code in [403, 404]

    def test_add_nonexistent_item_to_group(
        self, authenticated_client: TestClient, test_group: Group
    ):
        """
        Test: เพิ่ม item ที่ไม่มีในระบบเข้า group
        Expected: ได้รับ status 404
        """
        response = authenticated_client.post(
            f"/v1/group_item/group/my/{test_group.id}/items/99999"
        )

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_add_item_already_in_group(
        self, authenticated_client: TestClient, test_group: Group, test_group_item: Item
    ):
        """
        Test: เพิ่ม item ที่อยู่ใน group แล้ว
        Expected: ได้รับ status 403
        """
        response = authenticated_client.post(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_group_item.id}"
        )

        assert response.status_code == 403
        assert "already" in response.json()["detail"]

    def test_add_item_to_group_not_member(
        self,
        client: TestClient,
        db_session: Session,
        test_group: Group,
        test_item: Item,
    ):
        """
        Test: เพิ่ม item เข้า group โดยคนที่ไม่ได้เป็น member
        Expected: ได้รับ status 403
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง user ใหม่ที่ไม่ใช่ member
        another_user = User(
            username="nonmember",
            full_name="Non Member",
            email="nonmember@example.com",
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

        response = client.post(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_item.id}"
        )

        assert response.status_code == 403
        assert "not a member" in response.json()["detail"]

    def test_add_item_to_group_regular_member_cannot(
        self,
        client: TestClient,
        db_session: Session,
        test_group: Group,
        test_item: Item,
    ):
        """
        Test: เพิ่ม item เข้า group โดย regular member (ไม่ใช่ owner/admin)
        Expected: ได้รับ status 403
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง regular member
        member_user = User(
            username="regularmember",
            full_name="Regular Member",
            email="regular@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(member_user)
        db_session.commit()
        db_session.refresh(member_user)

        # เพิ่มเป็น member ธรรมดา
        member = GroupMember(
            group_id=test_group.id, user_id=member_user.id, role="member"
        )
        db_session.add(member)
        db_session.commit()

        # สร้าง token สำหรับ member
        token = create_access_token(
            data={"sub": member_user.username, "id": member_user.id}
        )
        client.headers = {"Authorization": f"Bearer {token}"}

        response = client.post(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_item.id}"
        )

        assert response.status_code == 403
        assert "don't have permission" in response.json()["detail"]

    def test_add_deleted_item_to_group(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_item: Item,
        db_session: Session,
    ):
        """
        Test: เพิ่ม item ที่ถูกลบแล้วเข้า group
        Expected: ได้รับ status 404
        """
        from datetime import datetime, timezone

        # ทำเครื่องหมาย item เป็นลบ
        test_item.deleted_at = datetime.now(timezone.utc)
        db_session.commit()

        response = authenticated_client.post(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_item.id}"
        )

        assert response.status_code == 404


class TestRemoveItemFromGroup:
    """Test suite for DELETE /v1/group_item/group/my/{group_id}/items/{item_id} endpoint"""

    def test_remove_item_from_group_requires_authentication(
        self, client: TestClient, test_group: Group, test_group_item: Item
    ):
        """
        Test: ลบ item ออกจาก group โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.delete(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_group_item.id}"
        )
        assert response.status_code == 401

    def test_remove_item_from_group_success(
        self,
        authenticated_client: TestClient,
        test_group: Group,
        test_group_item: Item,
        db_session: Session,
    ):
        """
        Test: ลบ item ออกจาก group สำเร็จ
        Expected: item ถูกลบออกจาก group (group_id = None)
        """
        response = authenticated_client.delete(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_group_item.id}"
        )

        assert response.status_code == 204

        # Verify in database
        db_session.refresh(test_group_item)
        assert test_group_item.group_id is None

    def test_remove_item_from_group_by_admin(
        self,
        client: TestClient,
        db_session: Session,
        test_group: Group,
        test_group_item: Item,
    ):
        """
        Test: ลบ item ออกจาก group โดย admin member
        Expected: สามารถลบได้สำเร็จ
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง admin user
        admin_user = User(
            username="adminuser2",
            full_name="Admin User 2",
            email="admin2@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)

        # เพิ่มเป็น admin member
        admin_member = GroupMember(
            group_id=test_group.id, user_id=admin_user.id, role="admin"
        )
        db_session.add(admin_member)
        db_session.commit()

        # สร้าง token สำหรับ admin
        token = create_access_token(
            data={"sub": admin_user.username, "id": admin_user.id}
        )
        client.headers = {"Authorization": f"Bearer {token}"}

        response = client.delete(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_group_item.id}"
        )

        assert response.status_code == 204

    def test_remove_item_from_nonexistent_group(
        self, authenticated_client: TestClient, test_group_item: Item
    ):
        """
        Test: ลบ item ออกจาก group ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.delete(
            f"/v1/group_item/group/my/99999/items/{test_group_item.id}"
        )

        assert response.status_code == 404

    def test_remove_nonexistent_item_from_group(
        self, authenticated_client: TestClient, test_group: Group
    ):
        """
        Test: ลบ item ที่ไม่มีในระบบออกจาก group
        Expected: ได้รับ status 404
        """
        response = authenticated_client.delete(
            f"/v1/group_item/group/my/{test_group.id}/items/99999"
        )

        assert response.status_code == 404

    def test_remove_item_not_in_group(
        self, authenticated_client: TestClient, test_group: Group, test_item: Item
    ):
        """
        Test: ลบ item ที่ไม่ได้อยู่ใน group
        Expected: ได้รับ status 404
        """
        response = authenticated_client.delete(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_item.id}"
        )

        assert response.status_code == 404

    def test_remove_item_from_group_not_member(
        self,
        client: TestClient,
        db_session: Session,
        test_group: Group,
        test_group_item: Item,
    ):
        """
        Test: ลบ item ออกจาก group โดยคนที่ไม่ได้เป็น member
        Expected: ได้รับ status 404 หรือ 403
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง user ใหม่ที่ไม่ใช่ member
        another_user = User(
            username="nonmember2",
            full_name="Non Member 2",
            email="nonmember2@example.com",
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
            f"/v1/group_item/group/my/{test_group.id}/items/{test_group_item.id}"
        )

        assert response.status_code in [403, 404]

    def test_remove_item_from_group_regular_member_cannot(
        self,
        client: TestClient,
        db_session: Session,
        test_group: Group,
        test_group_item: Item,
    ):
        """
        Test: ลบ item ออกจาก group โดย regular member (ไม่ใช่ owner/admin)
        Expected: ได้รับ status 404 หรือ 403
        """
        import bcrypt
        from app.core.security import create_access_token

        # สร้าง regular member
        member_user = User(
            username="regularmember2",
            full_name="Regular Member 2",
            email="regular2@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(member_user)
        db_session.commit()
        db_session.refresh(member_user)

        # เพิ่มเป็น member ธรรมดา
        member = GroupMember(
            group_id=test_group.id, user_id=member_user.id, role="member"
        )
        db_session.add(member)
        db_session.commit()

        # สร้าง token สำหรับ member
        token = create_access_token(
            data={"sub": member_user.username, "id": member_user.id}
        )
        client.headers = {"Authorization": f"Bearer {token}"}

        response = client.delete(
            f"/v1/group_item/group/my/{test_group.id}/items/{test_group_item.id}"
        )

        assert response.status_code in [403, 404]

    def test_remove_item_from_different_group(
        self,
        authenticated_client: TestClient,
        db_session: Session,
        test_user: User,
        test_group_item: Item,
    ):
        """
        Test: ลบ item ที่อยู่ใน group อื่น
        Expected: ได้รับ status 404
        """
        # สร้าง group อื่น
        another_group = Group(
            name="Another Group",
            description="Another group",
            image_url="https://example.com/another.jpg",
            owner_id=test_user.id,
            follower_count=0,
        )
        db_session.add(another_group)
        db_session.commit()
        db_session.refresh(another_group)

        # เพิ่ม owner member
        owner_member = GroupMember(
            group_id=another_group.id, user_id=test_user.id, role="owner"
        )
        db_session.add(owner_member)
        db_session.commit()

        response = authenticated_client.delete(
            f"/v1/group_item/group/my/{another_group.id}/items/{test_group_item.id}"
        )

        assert response.status_code == 404
