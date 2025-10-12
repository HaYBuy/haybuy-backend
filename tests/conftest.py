"""
Pytest configuration and shared fixtures for HaYBuy Backend tests
"""

import os
import pytest
from typing import Generator
from dotenv import load_dotenv
from pathlib import Path

# โหลด .env.test ก่อนที่จะ import app เพื่อให้ตั้งค่า environment variables ก่อน
test_env_path = Path(__file__).parent.parent / ".env.test"
load_dotenv(dotenv_path=test_env_path, override=True)

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.database import Base, get_db
from app.db.models.Users.User import User
from app.core.security import create_access_token
import bcrypt


# ใช้ SQLite in-memory database สำหรับการทดสอบ
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# สร้าง test engine
test_engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """
    สร้าง database session ใหม่สำหรับแต่ละ test
    จะ rollback หลังจาก test เสร็จ
    """
    # สร้างตารางทั้งหมด
    Base.metadata.create_all(bind=test_engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # ลบตารางทั้งหมดหลัง test เสร็จ
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    สร้าง TestClient สำหรับทดสอบ API endpoints
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """
    สร้าง test user ในฐานข้อมูล
    """
    hashed_password = bcrypt.hashpw("testpassword123".encode("utf-8"), bcrypt.gensalt())

    user = User(
        username="testuser",
        full_name="Test User",
        email="testuser@example.com",
        password=hashed_password.decode("utf-8"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_user_token(test_user: User) -> str:
    """
    สร้าง JWT token สำหรับ test user
    """
    return create_access_token(
        data={
            "sub": test_user.username,
            "id": test_user.id,
        }
    )


@pytest.fixture
def authenticated_client(client: TestClient, test_user_token: str) -> TestClient:
    """
    สร้าง TestClient ที่มี authentication header
    """
    client.headers = {**client.headers, "Authorization": f"Bearer {test_user_token}"}
    return client


@pytest.fixture
def test_user_credentials() -> dict:
    """
    ข้อมูล credentials สำหรับ test user
    """
    return {
        "username": "testuser",
        "password": "testpassword123",
        "email": "testuser@example.com",
        "full_name": "Test User",
    }


@pytest.fixture
def multiple_test_users(db_session: Session) -> list[User]:
    """
    สร้าง test users หลายคนในฐานข้อมูล
    """
    users = []
    for i in range(1, 6):
        hashed_password = bcrypt.hashpw(
            f"password{i}".encode("utf-8"), bcrypt.gensalt()
        )
        user = User(
            username=f"testuser{i}",
            full_name=f"Test User {i}",
            email=f"testuser{i}@example.com",
            password=hashed_password.decode("utf-8"),
            is_active=True,
        )
        db_session.add(user)
        users.append(user)

    db_session.commit()
    for user in users:
        db_session.refresh(user)

    return users


@pytest.fixture
def test_category(db_session: Session):
    """
    สร้าง test category สำหรับใช้ในหลาย test files
    """
    from app.db.models.Categorys.main import Category

    category = Category(name="Electronics", slug="electronics")
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_item(db_session: Session, test_user: User, test_category):
    """
    สร้าง test item สำหรับใช้ในหลาย test files
    """
    from app.db.models.items.item import Item

    item = Item(
        name="Test Item",
        description="Test item description",
        price=100.00,
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
def multiple_test_items(db_session: Session, test_user: User, test_category):
    """สร้าง test items หลายรายการ"""
    from app.db.models.items.item import Item
    from decimal import Decimal

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
