"""
Unit tests for transaction endpoints (สำคัญที่สุด: create และ get my transactions)
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from decimal import Decimal

from app.db.models.Users.User import User
from app.db.models.items.item import Item
from app.db.models.Categorys.main import Category
from app.db.models.Transactions.transaction_model import Transaction


@pytest.fixture
def test_seller(db_session: Session) -> User:
    """สร้าง seller user สำหรับ transaction"""
    import bcrypt

    seller = User(
        username="seller",
        full_name="Seller User",
        email="seller@example.com",
        password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
            "utf-8"
        ),
        is_active=True,
    )
    db_session.add(seller)
    db_session.commit()
    db_session.refresh(seller)
    return seller


@pytest.fixture
def test_seller_item(
    db_session: Session, test_seller: User, test_category: Category
) -> Item:
    """สร้าง item ของ seller"""
    item = Item(
        name="Seller Item",
        description="Item for sale",
        price=Decimal("100.00"),
        quantity=10,
        status="available",
        owner_id=test_seller.id,
        category_id=test_category.id,
    )
    db_session.add(item)
    db_session.commit()
    db_session.refresh(item)
    return item


@pytest.fixture
def test_transaction(
    db_session: Session, test_user: User, test_seller: User, test_seller_item: Item
) -> Transaction:
    """สร้าง test transaction"""
    transaction = Transaction(
        item_id=test_seller_item.id,
        seller_id=test_seller.id,
        buyer_id=test_user.id,
        status="pending",
        agreed_price=Decimal("100.00"),
        amount=1,
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


class TestCreateTransaction:
    """Test suite for POST /v1/transaction/ endpoint"""

    def test_create_transaction_requires_authentication(
        self, client: TestClient, test_seller_item: Item, test_seller: User
    ):
        """
        Test: สร้าง transaction โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        transaction_data = {
            "item_id": test_seller_item.id,
            "seller_id": test_seller.id,
            "amount": 1,
        }

        response = client.post("/v1/transaction/", json=transaction_data)
        assert response.status_code == 401

    def test_create_transaction_success(
        self,
        authenticated_client: TestClient,
        test_seller_item: Item,
        test_seller: User,
    ):
        """
        Test: สร้าง transaction ใหม่สำเร็จ
        Expected: ได้รับ transaction ที่สร้างพร้อม id และสถานะ pending
        """
        transaction_data = {
            "item_id": test_seller_item.id,
            "seller_id": test_seller.id,
            "amount": 2,
        }

        response = authenticated_client.post("/v1/transaction/", json=transaction_data)

        assert response.status_code == 200
        data = response.json()
        assert data["item_id"] == test_seller_item.id
        assert data["seller_id"] == test_seller.id
        assert data["status"] == "pending"
        assert float(data["agreed_price"]) == float(test_seller_item.price * 2)
        assert data["amount"] == 2
        assert "id" in data

    def test_create_transaction_with_item_not_found(
        self, authenticated_client: TestClient, test_seller: User
    ):
        """
        Test: สร้าง transaction กับ item ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        transaction_data = {"item_id": 99999, "seller_id": test_seller.id, "amount": 1}

        response = authenticated_client.post("/v1/transaction/", json=transaction_data)

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_create_transaction_with_seller_not_found(
        self, authenticated_client: TestClient, test_seller_item: Item
    ):
        """
        Test: สร้าง transaction กับ seller ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        transaction_data = {
            "item_id": test_seller_item.id,
            "seller_id": 99999,
            "amount": 1,
        }

        response = authenticated_client.post("/v1/transaction/", json=transaction_data)

        assert response.status_code == 404
        assert "seller not found" in response.json()["detail"]

    def test_create_transaction_with_own_item(
        self, authenticated_client: TestClient, test_item: Item, test_user: User
    ):
        """
        Test: สร้าง transaction กับ item ของตัวเอง
        Expected: ได้รับ status 403
        """
        transaction_data = {
            "item_id": test_item.id,
            "seller_id": test_user.id,
            "amount": 1,
        }

        response = authenticated_client.post("/v1/transaction/", json=transaction_data)

        assert response.status_code == 403
        assert (
            "cannot perform this action on your own item" in response.json()["detail"]
        )

    def test_create_transaction_insufficient_quantity(
        self,
        authenticated_client: TestClient,
        test_seller_item: Item,
        test_seller: User,
        db_session: Session,
    ):
        """
        Test: สร้าง transaction กับจำนวนที่มากกว่าสต็อก
        Expected: ได้รับ status 400
        """
        # ทำให้ quantity เหลือน้อย
        test_seller_item.quantity = 1
        db_session.commit()

        transaction_data = {
            "item_id": test_seller_item.id,
            "seller_id": test_seller.id,
            "amount": 5,  # มากกว่า quantity
        }

        response = authenticated_client.post("/v1/transaction/", json=transaction_data)

        assert response.status_code == 400
        assert "not available" in response.json()["detail"]

    def test_create_transaction_with_unavailable_item(
        self,
        authenticated_client: TestClient,
        test_seller_item: Item,
        test_seller: User,
        db_session: Session,
    ):
        """
        Test: สร้าง transaction กับ item ที่ status ไม่ใช่ available
        Expected: ได้รับ status 400
        """
        # เปลี่ยน status เป็น sold
        test_seller_item.status = "sold"
        db_session.commit()

        transaction_data = {
            "item_id": test_seller_item.id,
            "seller_id": test_seller.id,
            "amount": 1,
        }

        response = authenticated_client.post("/v1/transaction/", json=transaction_data)

        assert response.status_code == 400
        assert "not available" in response.json()["detail"]

    def test_create_transaction_with_missing_fields(
        self, authenticated_client: TestClient
    ):
        """
        Test: สร้าง transaction โดยขาด required fields
        Expected: ได้รับ status 422 validation error
        """
        response = authenticated_client.post("/v1/transaction/", json={})
        assert response.status_code == 422

    def test_create_transaction_with_zero_amount(
        self,
        authenticated_client: TestClient,
        test_seller_item: Item,
        test_seller: User,
    ):
        """
        Test: สร้าง transaction กับจำนวน 0
        Expected: ได้รับ status 422 validation error
        """
        transaction_data = {
            "item_id": test_seller_item.id,
            "seller_id": test_seller.id,
            "amount": 0,
        }

        response = authenticated_client.post("/v1/transaction/", json=transaction_data)
        assert response.status_code in [400, 422]

    def test_create_transaction_with_negative_amount(
        self,
        authenticated_client: TestClient,
        test_seller_item: Item,
        test_seller: User,
    ):
        """
        Test: สร้าง transaction กับจำนวนติดลบ
        Expected: ได้รับ status 422 validation error
        """
        transaction_data = {
            "item_id": test_seller_item.id,
            "seller_id": test_seller.id,
            "amount": -1,
        }

        response = authenticated_client.post("/v1/transaction/", json=transaction_data)
        assert response.status_code == 422


class TestGetMyTransactions:
    """Test suite for GET /v1/transaction/my endpoint"""

    def test_get_my_transactions_requires_authentication(self, client: TestClient):
        """
        Test: ดึง transactions ของตัวเองโดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.get("/v1/transaction/my")
        assert response.status_code == 401

    def test_get_my_transactions_empty(self, authenticated_client: TestClient):
        """
        Test: ดึง transactions เมื่อยังไม่มี transactions
        Expected: ได้รับ list ว่าง
        """
        response = authenticated_client.get("/v1/transaction/my")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_my_transactions_as_buyer(
        self, authenticated_client: TestClient, test_transaction: Transaction
    ):
        """
        Test: ดึง transactions ที่ตัวเองเป็น buyer
        Expected: ได้รับ list ของ transactions
        """
        response = authenticated_client.get("/v1/transaction/my")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(t["id"] == test_transaction.id for t in data)
        assert all("item_id" in t for t in data)
        assert all("seller_id" in t for t in data)
        assert all("buyer_id" in t for t in data)
        assert all("status" in t for t in data)

    def test_get_my_transactions_as_seller(
        self,
        client: TestClient,
        test_seller: User,
        test_transaction: Transaction,
        db_session: Session,
    ):
        """
        Test: ดึง transactions ที่ตัวเองเป็น seller
        Expected: ได้รับ list ของ transactions
        """
        from app.core.security import create_access_token

        # สร้าง token สำหรับ seller
        seller_token = create_access_token(
            data={"sub": test_seller.username, "id": test_seller.id}
        )

        client.headers = {"Authorization": f"Bearer {seller_token}"}
        response = client.get("/v1/transaction/my")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert any(t["id"] == test_transaction.id for t in data)

    def test_get_my_transactions_both_roles(
        self,
        authenticated_client: TestClient,
        test_user: User,
        test_seller: User,
        test_seller_item: Item,
        db_session: Session,
    ):
        """
        Test: ดึง transactions ที่ตัวเองเป็นทั้ง buyer และ seller
        Expected: ได้รับ transactions ทั้งสองประเภท
        """
        # สร้าง transaction ที่เป็น buyer
        transaction1 = Transaction(
            item_id=test_seller_item.id,
            seller_id=test_seller.id,
            buyer_id=test_user.id,
            status="pending",
            agreed_price=Decimal("100.00"),
            amount=1,
        )
        db_session.add(transaction1)

        # สร้าง item ของตัวเอง
        category = Category(name="Cat", slug="cat")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        my_item = Item(
            name="My Item",
            description="My item for sale",
            price=Decimal("50.00"),
            quantity=5,
            status="available",
            owner_id=test_user.id,
            category_id=category.id,
        )
        db_session.add(my_item)
        db_session.commit()
        db_session.refresh(my_item)

        # สร้าง transaction ที่เป็น seller
        transaction2 = Transaction(
            item_id=my_item.id,
            seller_id=test_user.id,
            buyer_id=test_seller.id,
            status="pending",
            agreed_price=Decimal("50.00"),
            amount=1,
        )
        db_session.add(transaction2)
        db_session.commit()

        response = authenticated_client.get("/v1/transaction/my")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 2

        # ตรวจสอบว่ามีทั้ง transaction ที่เป็น buyer และ seller
        transaction_ids = [t["id"] for t in data]
        assert transaction1.id in transaction_ids
        assert transaction2.id in transaction_ids

    def test_get_my_transactions_excludes_others(
        self, authenticated_client: TestClient, db_session: Session
    ):
        """
        Test: ดึง transactions ต้องไม่แสดง transactions ของคนอื่น
        Expected: ไม่มี transactions ของคนอื่น
        """
        # สร้าง users และ transaction ของคนอื่น
        import bcrypt

        user1 = User(
            username="user1",
            full_name="User 1",
            email="user1@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        user2 = User(
            username="user2",
            full_name="User 2",
            email="user2@example.com",
            password=bcrypt.hashpw("password".encode("utf-8"), bcrypt.gensalt()).decode(
                "utf-8"
            ),
            is_active=True,
        )
        db_session.add_all([user1, user2])
        db_session.commit()

        category = Category(name="Cat2", slug="cat2")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)

        item = Item(
            name="Other Item",
            description="Item",
            price=Decimal("100.00"),
            quantity=10,
            status="available",
            owner_id=user1.id,
            category_id=category.id,
        )
        db_session.add(item)
        db_session.commit()
        db_session.refresh(item)

        other_transaction = Transaction(
            item_id=item.id,
            seller_id=user1.id,
            buyer_id=user2.id,
            status="pending",
            agreed_price=Decimal("100.00"),
            amount=1,
        )
        db_session.add(other_transaction)
        db_session.commit()

        response = authenticated_client.get("/v1/transaction/my")

        assert response.status_code == 200
        data = response.json()
        transaction_ids = [t["id"] for t in data]
        assert other_transaction.id not in transaction_ids
