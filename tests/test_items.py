"""
Unit tests for item endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.models.Users.User import User
from app.db.models.items.item import Item
from app.db.models.Categorys.main import Category


@pytest.fixture
def test_category(db_session: Session) -> Category:
    """สร้าง test category"""
    category = Category(name="Electronics", description="Electronic items")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_item(db_session: Session, test_user: User, test_category: Category) -> Item:
    """สร้าง test item"""
    item = Item(
        name="Test Item",
        description="Test item description",
        price=Decimal("99.99"),
        quantity=10,
        status="available",
        owner_id=test_user.id,
        category_id=test_category.id,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def multiple_test_items(
    db_session: Session, test_user: User, test_category: Category
) -> list[Item]:
    """สร้าง test items หลายรายการ"""
    items = []
    for i in range(1, 6):
        item = Item(
            name=f"Test Item {i}",
            description=f"Description for item {i}",
            price=Decimal(f"{i * 10}.99"),
            quantity=i * 5,
            status="available",
            owner_id=test_user.id,
            category_id=test_category.id,
        )
        db_session.add(item)
        items.append(item)

    db_session.commit()
    for item in items:
        db_session.refresh(item)

    return items


class TestListItems:
    """Test suite for GET /v1/item/ endpoint"""

    def test_list_items_empty_database(self, client: TestClient):
        """
        Test: ดึง list items เมื่อยังไม่มี items
        Expected: ได้รับ list ว่าง
        """
        response = client.get("/v1/item/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_items_with_data(
        self, client: TestClient, multiple_test_items: list[Item]
    ):
        """
        Test: ดึง list items ทั้งหมด
        Expected: ได้รับ list ของ items
        """
        response = client.get("/v1/item/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all("id" in item for item in data)
        assert all("name" in item for item in data)
        assert all("price" in item for item in data)

    def test_list_items_with_search(
        self, client: TestClient, multiple_test_items: list[Item]
    ):
        """
        Test: ค้นหา items ด้วย search query
        Expected: ได้รับเฉพาะ items ที่ตรงกับ search
        """
        response = client.get("/v1/item/?search=Item 1")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert "Item 1" in data[0]["name"]

    def test_list_items_with_price_range(
        self, client: TestClient, multiple_test_items: list[Item]
    ):
        """
        Test: กรอง items ด้วยช่วงราคา
        Expected: ได้รับเฉพาะ items ที่อยู่ในช่วงราคา
        """
        response = client.get("/v1/item/?min_price=20&max_price=40")

        assert response.status_code == 200
        data = response.json()

        # ตรวจสอบว่าราคาทั้งหมดอยู่ในช่วง
        for item in data:
            price = float(item["price"])
            assert 20 <= price <= 40

    def test_list_items_with_category_filter(
        self, client: TestClient, test_item: Item, test_category: Category
    ):
        """
        Test: กรอง items ด้วย category_id
        Expected: ได้รับเฉพาะ items ในหมวดหมู่นั้น
        """
        response = client.get(f"/v1/item/?category_id={test_category.id}")

        assert response.status_code == 200
        data = response.json()
        assert all(item["category_id"] == test_category.id for item in data)

    def test_list_items_with_pagination(
        self, client: TestClient, multiple_test_items: list[Item]
    ):
        """
        Test: ใช้ pagination (skip และ limit)
        Expected: ได้รับ items ตามจำนวนที่กำหนด
        """
        response = client.get("/v1/item/?skip=0&limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # ทดสอบหน้าถัดไป
        response2 = client.get("/v1/item/?skip=3&limit=3")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 2  # เหลืออีก 2 items


class TestGetItemById:
    """Test suite for GET /v1/item/{item_id} endpoint"""

    def test_get_item_by_id_success(self, client: TestClient, test_item: Item):
        """
        Test: ดึงข้อมูล item ด้วย ID ที่มีอยู่
        Expected: ได้รับข้อมูล item ที่ถูกต้อง
        """
        response = client.get(f"/v1/item/{test_item.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_item.id
        assert data["name"] == test_item.name
        assert float(data["price"]) == float(test_item.price)
        assert data["quantity"] == test_item.quantity

    def test_get_item_by_id_not_found(self, client: TestClient):
        """
        Test: ดึงข้อมูล item ด้วย ID ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = client.get("/v1/item/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"

    def test_get_deleted_item_not_found(
        self, client: TestClient, test_item: Item, db_session: Session
    ):
        """
        Test: ดึงข้อมูล item ที่ถูก soft delete แล้ว
        Expected: ได้รับ status 404
        """
        from datetime import datetime

        # ทำเครื่องหมาย item เป็นลบ
        test_item.deleted_at = datetime.utcnow()
        db_session.commit()

        response = client.get(f"/v1/item/{test_item.id}")

        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"


class TestGetItemsByUser:
    """Test suite for GET /v1/item/user/{user_id} endpoint"""

    def test_get_items_by_user_success(
        self, client: TestClient, test_user: User, multiple_test_items: list[Item]
    ):
        """
        Test: ดึง items ทั้งหมดของ user
        Expected: ได้รับ items ของ user นั้น
        """
        response = client.get(f"/v1/item/user/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all(item["owner_id"] == test_user.id for item in data)

    def test_get_items_by_user_empty(self, client: TestClient, test_user: User):
        """
        Test: ดึง items ของ user ที่ยังไม่มี items
        Expected: ได้รับ list ว่าง
        """
        response = client.get(f"/v1/item/user/{test_user.id}")

        assert response.status_code == 200
        assert response.json() == []


class TestGetPriceHistories:
    """Test suite for GET /v1/item/my/{item_id}/pricehistories endpoint"""

    def test_get_price_histories_requires_authentication(
        self, client: TestClient, test_item: Item
    ):
        """
        Test: ดึง price histories โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.get(f"/v1/item/my/{test_item.id}/pricehistories")

        assert response.status_code == 401

    def test_get_price_histories_item_not_found(self, authenticated_client: TestClient):
        """
        Test: ดึง price histories ของ item ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.get("/v1/item/my/99999/pricehistories")

        assert response.status_code == 404
        assert response.json()["detail"] == "Item not found"

    def test_get_price_histories_empty(
        self, authenticated_client: TestClient, test_item: Item
    ):
        """
        Test: ดึง price histories เมื่อยังไม่มี history
        Expected: ได้รับ list ว่าง
        """
        response = authenticated_client.get(
            f"/v1/item/my/{test_item.id}/pricehistories"
        )

        assert response.status_code == 200
        assert response.json() == []


class TestItemValidation:
    """Test suite for item data validation"""

    def test_get_item_with_invalid_id_type(self, client: TestClient):
        """
        Test: ดึงข้อมูล item ด้วย ID ที่ไม่ใช่ตัวเลข
        Expected: ได้รับ status 422
        """
        response = client.get("/v1/item/invalid_id")

        assert response.status_code == 422

    def test_list_items_with_invalid_price_range(self, client: TestClient):
        """
        Test: กรอง items ด้วยช่วงราคาที่ไม่ถูกต้อง (max < min)
        Expected: ได้รับ list ว่าง หรือ ไม่มี items ที่ตรงเงื่อนไข
        """
        response = client.get("/v1/item/?min_price=100&max_price=50")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestCreateItem:
    """Test suite for POST /v1/item/my endpoint"""

    def test_create_item_requires_authentication(self, client: TestClient):
        """
        Test: สร้าง item โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        item_data = {
            "name": "New Item",
            "description": "New item description",
            "price": 99.99,
            "quantity": 10,
            "status": "available",
            "category_id": 1,
        }

        response = client.post("/v1/item/my", json=item_data)
        assert response.status_code == 401

    def test_create_item_success(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        db_session: Session,
    ):
        """
        Test: สร้าง item ใหม่สำเร็จ
        Expected: ได้รับ item ที่สร้างพร้อม id และสร้าง price history
        """
        item_data = {
            "name": "New Product",
            "description": "A brand new product",
            "price": 199.99,
            "quantity": 25,
            "status": "available",
            "category_id": test_category.id,
        }

        response = authenticated_client.post("/v1/item/my", json=item_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Product"
        assert float(data["price"]) == 199.99
        assert data["quantity"] == 25
        assert data["status"] == "available"
        assert "id" in data

    def test_create_item_duplicate_name_same_user(
        self, authenticated_client: TestClient, test_item: Item
    ):
        """
        Test: สร้าง item ด้วยชื่อที่ user คนเดียวกันมีอยู่แล้ว
        Expected: ได้รับ status 403
        """
        item_data = {
            "name": test_item.name,
            "description": "Different description",
            "price": 50.00,
            "quantity": 5,
            "status": "available",
            "category_id": test_item.category_id,
        }

        response = authenticated_client.post("/v1/item/my", json=item_data)

        assert response.status_code == 403
        assert "already exist" in response.json()["detail"]

    def test_create_item_with_missing_required_fields(
        self, authenticated_client: TestClient
    ):
        """
        Test: สร้าง item โดยขาด required fields
        Expected: ได้รับ status 422 validation error
        """
        response = authenticated_client.post("/v1/item/my", json={})
        assert response.status_code == 422

    def test_create_item_with_negative_price(
        self, authenticated_client: TestClient, test_category: Category
    ):
        """
        Test: สร้าง item ด้วยราคาติดลบ
        Expected: ได้รับ status 422 validation error
        """
        item_data = {
            "name": "Invalid Price Item",
            "description": "Item with negative price",
            "price": -10.00,
            "quantity": 10,
            "status": "available",
            "category_id": test_category.id,
        }

        response = authenticated_client.post("/v1/item/my", json=item_data)
        assert response.status_code == 422


class TestUpdateItem:
    """Test suite for PUT /v1/item/my/{item_id} endpoint"""

    def test_update_item_requires_authentication(
        self, client: TestClient, test_item: Item, test_category: Category
    ):
        """
        Test: อัพเดท item โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        update_data = {
            "name": "Updated Item",
            "description": "Updated description",
            "price": 150.00,
            "quantity": 15,
            "status": "available",
            "category_id": test_category.id,
        }

        response = client.put(f"/v1/item/my/{test_item.id}", json=update_data)
        assert response.status_code == 401

    def test_update_item_success(
        self,
        authenticated_client: TestClient,
        test_item: Item,
        test_category: Category,
        db_session: Session,
    ):
        """
        Test: อัพเดท item ของตัวเองสำเร็จ
        Expected: ข้อมูล item ถูกอัพเดท
        """
        update_data = {
            "name": "Updated Item Name",
            "description": "Updated description",
            "price": 149.99,
            "quantity": 20,
            "status": "available",
            "category_id": test_category.id,
        }

        response = authenticated_client.put(
            f"/v1/item/my/{test_item.id}", json=update_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Item Name"
        assert float(data["price"]) == 149.99
        assert data["quantity"] == 20

        # Verify in database
        db_session.refresh(test_item)
        assert test_item.name == "Updated Item Name"

    def test_update_item_price_creates_history(
        self,
        authenticated_client: TestClient,
        test_item: Item,
        test_category: Category,
        db_session: Session,
    ):
        """
        Test: อัพเดทราคา item ต้องสร้าง price history
        Expected: มี price history ใหม่ในฐานข้อมูล
        """
        from app.db.models.PriceHistorys.main import PriceHistory
        from decimal import Decimal

        # นับจำนวน price histories ก่อนอัพเดท
        old_count = (
            db_session.query(PriceHistory)
            .filter(PriceHistory.item_id == test_item.id)
            .count()
        )

        update_data = {
            "name": test_item.name,
            "description": test_item.description,
            "price": 299.99,  # ราคาใหม่
            "quantity": test_item.quantity,
            "status": "available",
            "category_id": test_category.id,
        }

        response = authenticated_client.put(
            f"/v1/item/my/{test_item.id}", json=update_data
        )

        assert response.status_code == 200

        # ตรวจสอบว่ามี price history เพิ่มขึ้น
        new_count = (
            db_session.query(PriceHistory)
            .filter(PriceHistory.item_id == test_item.id)
            .count()
        )
        assert new_count == old_count + 1

    def test_update_item_not_found(
        self, authenticated_client: TestClient, test_category: Category
    ):
        """
        Test: อัพเดท item ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        update_data = {
            "name": "Item",
            "description": "Description",
            "price": 100.00,
            "quantity": 10,
            "status": "available",
            "category_id": test_category.id,
        }

        response = authenticated_client.put("/v1/item/my/99999", json=update_data)
        assert response.status_code == 404

    def test_update_item_not_owner(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        db_session: Session,
        test_user: User,
    ):
        """
        Test: อัพเดท item ที่ไม่ใช่ของตัวเอง
        Expected: ได้รับ status 403
        """
        # สร้าง item ของ user อื่น
        import bcrypt

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

        another_item = Item(
            name="Another Item",
            description="Not my item",
            price=Decimal("50.00"),
            quantity=5,
            status="available",
            owner_id=another_user.id,
            category_id=test_category.id,
        )
        db_session.add(another_item)
        db_session.commit()
        db_session.refresh(another_item)

        update_data = {
            "name": "Trying to Update",
            "description": "Should fail",
            "price": 100.00,
            "quantity": 10,
            "status": "available",
            "category_id": test_category.id,
        }

        response = authenticated_client.put(
            f"/v1/item/my/{another_item.id}", json=update_data
        )

        assert response.status_code == 403
        assert "not allowed" in response.json()["detail"]


class TestDeleteItem:
    """Test suite for DELETE /v1/item/my/{item_id} endpoint"""

    def test_delete_item_requires_authentication(
        self, client: TestClient, test_item: Item
    ):
        """
        Test: ลบ item โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.delete(f"/v1/item/my/{test_item.id}")
        assert response.status_code == 401

    def test_delete_item_success(
        self, authenticated_client: TestClient, test_item: Item, db_session: Session
    ):
        """
        Test: ลบ item ของตัวเองสำเร็จ (soft delete)
        Expected: item ถูก soft delete
        """
        item_id = test_item.id

        response = authenticated_client.delete(f"/v1/item/my/{item_id}")

        assert response.status_code == 200
        assert "deleted" in response.json()["detail"]

        # Verify soft deleted
        db_session.refresh(test_item)
        assert test_item.deleted_at is not None

    def test_delete_item_not_found(self, authenticated_client: TestClient):
        """
        Test: ลบ item ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.delete("/v1/item/my/99999")
        assert response.status_code == 404

    def test_delete_item_not_owner(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        db_session: Session,
    ):
        """
        Test: ลบ item ที่ไม่ใช่ของตัวเอง
        Expected: ได้รับ status 403
        """
        # สร้าง item ของ user อื่น
        import bcrypt

        another_user = User(
            username="anotheruser4",
            full_name="Another User 4",
            email="another4@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add(another_user)
        db_session.commit()

        another_item = Item(
            name="Another Item 2",
            description="Not my item",
            price=Decimal("50.00"),
            quantity=5,
            status="available",
            owner_id=another_user.id,
            category_id=test_category.id,
        )
        db_session.add(another_item)
        db_session.commit()
        db_session.refresh(another_item)

        response = authenticated_client.delete(f"/v1/item/my/{another_item.id}")

        assert response.status_code == 403
        assert "not allowed" in response.json()["detail"]


class TestPatchItemStatus:
    """Test suite for PATCH /v1/item/my/{item_id}/status endpoint"""

    def test_patch_item_status_requires_authentication(
        self, client: TestClient, test_item: Item
    ):
        """
        Test: เปลี่ยน status ของ item โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.patch(
            f"/v1/item/my/{test_item.id}/status", json={"status": "sold"}
        )
        assert response.status_code == 401

    def test_patch_item_status_success(
        self, authenticated_client: TestClient, test_item: Item, db_session: Session
    ):
        """
        Test: เปลี่ยน status ของ item สำเร็จ
        Expected: status ถูกอัพเดท
        """
        response = authenticated_client.patch(
            f"/v1/item/my/{test_item.id}/status", json={"status": "sold"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "sold"

        # Verify in database
        db_session.refresh(test_item)
        assert test_item.status == "sold"

    def test_patch_item_status_not_found(self, authenticated_client: TestClient):
        """
        Test: เปลี่ยน status ของ item ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = authenticated_client.patch(
            "/v1/item/my/99999/status", json={"status": "sold"}
        )
        assert response.status_code == 404

    def test_patch_item_status_invalid_status(
        self, authenticated_client: TestClient, test_item: Item
    ):
        """
        Test: เปลี่ยน status เป็นค่าที่ไม่ valid
        Expected: ได้รับ status 422 validation error
        """
        response = authenticated_client.patch(
            f"/v1/item/my/{test_item.id}/status", json={"status": "invalid_status"}
        )
        assert response.status_code == 422
