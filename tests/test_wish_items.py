"""
Unit tests for wish item endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.models.Users.User import User
from app.db.models.items.item import Item
from app.db.models.items.wishItem import WishItem
from app.db.models.Categorys.main import Category


@pytest.fixture
def test_wish_item(db_session: Session, test_user: User, test_item: Item) -> WishItem:
    """สร้าง test wish item"""
    wish_item = WishItem(user_id=test_user.id, item_id=test_item.id, privacy="private")
    db_session.add(wish_item)
    db_session.commit()
    db_session.refresh(wish_item)
    return wish_item


@pytest.fixture
def multiple_test_wish_items(
    db_session: Session, test_user: User, multiple_test_items: list[Item]
) -> list[WishItem]:
    """สร้าง test wish items หลายรายการ"""
    wish_items = []
    for i, item in enumerate(multiple_test_items[:3]):
        wish_item = WishItem(
            user_id=test_user.id,
            item_id=item.id,
            privacy="public" if i % 2 == 0 else "private",
        )
        db_session.add(wish_item)
        wish_items.append(wish_item)

    db_session.commit()
    for wish_item in wish_items:
        db_session.refresh(wish_item)

    return wish_items


class TestAddWishItem:
    """Test suite for POST /v1/wish-item/ endpoint"""

    def test_add_wish_item_requires_authentication(
        self, client: TestClient, test_item: Item
    ):
        """
        Test: เพิ่ม item ไป wish list โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        wish_data = {"item_id": test_item.id}

        response = client.post("/v1/wish-item/", json=wish_data)
        assert response.status_code == 401

    def test_add_wish_item_success(
        self, authenticated_client: TestClient, test_item: Item
    ):
        """
        Test: เพิ่ม item ไป wish list สำเร็จ
        Expected: ได้รับ wish item ที่สร้าง
        """
        wish_data = {"item_id": test_item.id}

        response = authenticated_client.post("/v1/wish-item/", json=wish_data)

        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == test_item.id
        assert "id" in data
        assert "user_id" in data

    def test_add_wish_item_duplicate(
        self, authenticated_client: TestClient, test_wish_item: WishItem
    ):
        """
        Test: เพิ่ม item ที่มีใน wish list อยู่แล้ว
        Expected: ได้รับ status 403
        """
        wish_data = {"item_id": test_wish_item.item_id}

        response = authenticated_client.post("/v1/wish-item/", json=wish_data)

        assert response.status_code == 403
        assert "already in wish list" in response.json()["detail"]

    def test_add_wish_item_with_missing_fields(self, authenticated_client: TestClient):
        """
        Test: เพิ่ม wish item โดยขาด required fields
        Expected: ได้รับ status 422 validation error
        """
        response = authenticated_client.post("/v1/wish-item/", json={})
        assert response.status_code == 422

    def test_add_wish_item_nonexistent_item(self, authenticated_client: TestClient):
        """
        Test: เพิ่ม item ที่ไม่มีในระบบไป wish list
        Expected: อาจจะ success หรือ error ขึ้นกับ validation
        """
        wish_data = {"item_id": 99999}

        response = authenticated_client.post("/v1/wish-item/", json=wish_data)
        # อาจจะ 200, 404, หรือ 422 ขึ้นกับ implementation
        assert response.status_code in [200, 404, 422]


class TestRemoveWishItem:
    """Test suite for DELETE /v1/wish-item/my/{wish_id} endpoint"""

    def test_remove_wish_item_requires_authentication(
        self, client: TestClient, test_wish_item: WishItem
    ):
        """
        Test: ลบ wish item โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.delete(f"/v1/wish-item/my/{test_wish_item.id}")
        assert response.status_code == 401

    def test_remove_wish_item_success(
        self,
        authenticated_client: TestClient,
        test_wish_item: WishItem,
        db_session: Session,
    ):
        """
        Test: ลบ wish item สำเร็จ
        Expected: wish item ถูกลบจากฐานข้อมูล
        """
        wish_id = test_wish_item.id

        response = authenticated_client.delete(f"/v1/wish-item/my/{wish_id}")

        assert response.status_code == 200
        assert "deleted" in response.json()["detail"]

        # Verify deleted from database
        deleted_wish = db_session.query(WishItem).filter(WishItem.id == wish_id).first()
        assert deleted_wish is None

    def test_remove_wish_item_not_found(self, authenticated_client: TestClient):
        """
        Test: ลบ wish item ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.delete("/v1/wish-item/my/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"

    def test_remove_wish_item_not_owner(
        self, authenticated_client: TestClient, db_session: Session, test_item: Item
    ):
        """
        Test: ลบ wish item ที่ไม่ใช่ของตัวเอง
        Expected: ได้รับ status 404
        """
        # สร้าง wish item ของ user อื่น
        import bcrypt

        another_user = User(
            username="anotheruser5",
            full_name="Another User 5",
            email="another5@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(another_user)
        db_session.commit()

        another_wish = WishItem(
            user_id=another_user.id, item_id=test_item.id, privacy="private"
        )
        db_session.add(another_wish)
        db_session.commit()
        db_session.refresh(another_wish)

        response = authenticated_client.delete(f"/v1/wish-item/my/{another_wish.id}")

        assert response.status_code == 404


class TestSetPrivacyWishItem:
    """Test suite for PATCH /v1/wish-item/my/{wish_id}/privacy endpoint"""

    def test_set_privacy_requires_authentication(
        self, client: TestClient, test_wish_item: WishItem
    ):
        """
        Test: เปลี่ยน privacy ของ wish item โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.patch(f"/v1/wish-item/my/{test_wish_item.id}/privacy")
        assert response.status_code == 401

    def test_toggle_privacy_from_private_to_public(
        self,
        authenticated_client: TestClient,
        test_wish_item: WishItem,
        db_session: Session,
    ):
        """
        Test: เปลี่ยน privacy จาก private เป็น public
        Expected: privacy ถูกเปลี่ยน
        """
        # Ensure it starts as private
        test_wish_item.privacy = "private"
        db_session.commit()

        response = authenticated_client.patch(
            f"/v1/wish-item/my/{test_wish_item.id}/privacy"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["privacy"] == "public"

        # Verify in database
        db_session.refresh(test_wish_item)
        assert test_wish_item.privacy == "public"

    def test_toggle_privacy_from_public_to_private(
        self,
        authenticated_client: TestClient,
        test_wish_item: WishItem,
        db_session: Session,
    ):
        """
        Test: เปลี่ยน privacy จาก public เป็น private
        Expected: privacy ถูกเปลี่ยน
        """
        # Ensure it starts as public
        test_wish_item.privacy = "public"
        db_session.commit()

        response = authenticated_client.patch(
            f"/v1/wish-item/my/{test_wish_item.id}/privacy"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["privacy"] == "private"

        # Verify in database
        db_session.refresh(test_wish_item)
        assert test_wish_item.privacy == "private"

    def test_set_privacy_not_found(self, authenticated_client: TestClient):
        """
        Test: เปลี่ยน privacy ของ wish item ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.patch("/v1/wish-item/my/99999/privacy")

        assert response.status_code == 404
        assert response.json()["detail"] == "Wish item not found"

    def test_set_privacy_not_owner(
        self, authenticated_client: TestClient, db_session: Session, test_item: Item
    ):
        """
        Test: เปลี่ยน privacy ของ wish item ที่ไม่ใช่ของตัวเอง
        Expected: ได้รับ status 403
        """
        # สร้าง wish item ของ user อื่น
        import bcrypt

        another_user = User(
            username="anotheruser6",
            full_name="Another User 6",
            email="another6@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(another_user)
        db_session.commit()

        another_wish = WishItem(
            user_id=another_user.id, item_id=test_item.id, privacy="private"
        )
        db_session.add(another_wish)
        db_session.commit()
        db_session.refresh(another_wish)

        response = authenticated_client.patch(
            f"/v1/wish-item/my/{another_wish.id}/privacy"
        )

        assert response.status_code == 403
        assert "Not allowed" in response.json()["detail"]


class TestGetMyWishListItems:
    """Test suite for GET /v1/wish-item/my/items endpoint"""

    def test_get_my_wish_list_items_requires_authentication(self, client: TestClient):
        """
        Test: ดึง items ใน wish list โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.get("/v1/wish-item/my/items")
        assert response.status_code == 401

    def test_get_my_wish_list_items_empty(self, authenticated_client: TestClient):
        """
        Test: ดึง items ใน wish list เมื่อยังไม่มี wish items
        Expected: ได้รับ list ว่าง
        """
        response = authenticated_client.get("/v1/wish-item/my/items")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_my_wish_list_items_with_data(
        self, authenticated_client: TestClient, multiple_test_wish_items: list[WishItem]
    ):
        """
        Test: ดึง items ใน wish list ของตัวเอง
        Expected: ได้รับ list ของ items
        """
        response = authenticated_client.get("/v1/wish-item/my/items")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in item for item in data)
        assert all("name" in item for item in data)

    def test_get_my_wish_list_items_with_pagination(
        self, authenticated_client: TestClient, multiple_test_wish_items: list[WishItem]
    ):
        """
        Test: ใช้ pagination (skip และ limit)
        Expected: ได้รับ items ตามจำนวนที่กำหนด
        """
        response = authenticated_client.get("/v1/wish-item/my/items?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestGetMyWishList:
    """Test suite for GET /v1/wish-item/my endpoint"""

    def test_get_my_wish_list_requires_authentication(self, client: TestClient):
        """
        Test: ดึง wish list โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.get("/v1/wish-item/my")
        assert response.status_code == 401

    def test_get_my_wish_list_empty(self, authenticated_client: TestClient):
        """
        Test: ดึง wish list เมื่อยังไม่มี wish items
        Expected: ได้รับ list ว่าง
        """
        response = authenticated_client.get("/v1/wish-item/my")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_my_wish_list_with_data(
        self, authenticated_client: TestClient, multiple_test_wish_items: list[WishItem]
    ):
        """
        Test: ดึง wish list ของตัวเอง
        Expected: ได้รับ list ของ wish items
        """
        response = authenticated_client.get("/v1/wish-item/my")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("id" in wish for wish in data)
        assert all("item_id" in wish for wish in data)
        assert all("user_id" in wish for wish in data)
        assert all("privacy" in wish for wish in data)

    def test_get_my_wish_list_with_pagination(
        self, authenticated_client: TestClient, multiple_test_wish_items: list[WishItem]
    ):
        """
        Test: ใช้ pagination (skip และ limit)
        Expected: ได้รับ wish items ตามจำนวนที่กำหนด
        """
        response = authenticated_client.get("/v1/wish-item/my?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2


class TestShareWishList:
    """Test suite for GET /v1/wish-item/my/share/{target_id} endpoint"""

    def test_share_wish_list_public_access(
        self,
        client: TestClient,
        test_user: User,
        multiple_test_wish_items: list[WishItem],
    ):
        """
        Test: ดูฃ wish list ของ user อื่น (public access)
        Expected: ได้รับเฉพาะ wish items ที่เป็น public
        """
        response = client.get(f"/v1/wish-item/my/share/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        # ควรได้เฉพาะ public items (2 items จาก fixture)
        assert all(wish["privacy"] == "public" for wish in data)

    def test_share_wish_list_empty_user(self, client: TestClient):
        """
        Test: ดู wish list ของ user ที่ไม่มี wish items
        Expected: ได้รับ list ว่าง
        """
        response = client.get("/v1/wish-item/my/share/99999")

        assert response.status_code == 200
        assert response.json() == []

    def test_share_wish_list_excludes_private(
        self, client: TestClient, test_user: User, db_session: Session, test_item: Item
    ):
        """
        Test: ดู wish list ต้องไม่แสดง private items
        Expected: ไม่มี private items ในผลลัพธ์
        """
        # สร้าง private wish item
        private_wish = WishItem(
            user_id=test_user.id, item_id=test_item.id, privacy="private"
        )
        db_session.add(private_wish)
        db_session.commit()

        response = client.get(f"/v1/wish-item/my/share/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        # ไม่ควรมี private items
        wish_ids = [wish["id"] for wish in data]
        assert private_wish.id not in wish_ids

    def test_share_wish_list_with_pagination(
        self,
        client: TestClient,
        test_user: User,
        multiple_test_wish_items: list[WishItem],
    ):
        """
        Test: ใช้ pagination (skip และ limit)
        Expected: ได้รับ wish items ตามจำนวนที่กำหนด
        """
        response = client.get(f"/v1/wish-item/my/share/{test_user.id}?skip=0&limit=1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1
