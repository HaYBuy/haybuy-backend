# 🧪 Testing Guide - HaYBuy Backend

## 📖 Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Setup Testing Environment](#setup-testing-environment)
- [Running Tests](#running-tests)
- [Writing Tests](#writing-tests)
- [Test Coverage](#test-coverage)

---

## 🎯 Overview

This guide explains how to set up and run tests for the HaYBuy Backend API.

### Testing Stack

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **httpx**: HTTP client for testing FastAPI
- **faker**: Generate fake data
- **factory-boy**: Create test fixtures (optional)

---

## 📁 Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Shared fixtures
├── test_auth.py               # Authentication tests
├── test_users.py              # User endpoint tests
├── test_items.py              # Item endpoint tests
├── test_categories.py         # Category tests
├── test_groups.py             # Group tests
├── test_transactions.py       # Transaction tests
└── fixtures/
    ├── __init__.py
    ├── user_fixtures.py       # User-related fixtures
    └── item_fixtures.py       # Item-related fixtures
```

---

## ⚙️ Setup Testing Environment

### 1. Install Test Dependencies

Add to `requirements.txt`:

```txt
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
httpx>=0.24.0
faker>=19.0.0
pytest-cov>=4.1.0
```

Install:

```bash
pip install -r requirements.txt
```

### 2. Create Test Database

Use a separate database for testing:

```env
# .env.test
DATABASE_URL=postgresql+psycopg2://admin:admin@localhost:5432/haybuy_test_db
```

### 3. Create conftest.py

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.database import Base, get_db
from app.core.security import create_access_token

# Test database URL
TEST_DATABASE_URL = "postgresql+psycopg2://admin:admin@localhost:5432/haybuy_test_db"

# Create test engine
engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    """Create a test client with database override"""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_user(db):
    """Create a test user"""
    from app.db.models.Users.User import User
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=pwd_context.hash("testpass123"),
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@pytest.fixture
def auth_token(test_user):
    """Create authentication token for test user"""
    return create_access_token({"sub": test_user.username, "id": test_user.id})

@pytest.fixture
def auth_headers(auth_token):
    """Create authentication headers"""
    return {"Authorization": f"Bearer {auth_token}"}
```

---

## 🏃 Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_auth.py
```

### Run Specific Test Function

```bash
pytest tests/test_auth.py::test_login_success
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Only Failed Tests

```bash
pytest --lf
```

---

## ✍️ Writing Tests

### Example: Authentication Tests

```python
# tests/test_auth.py
import pytest
from fastapi import status

class TestAuthentication:

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post(
            "/v1/auth/token",
            data={
                "username": "testuser",
                "password": "testpass123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client, test_user):
        """Test login with invalid credentials"""
        response = client.post(
            "/v1/auth/token",
            data={
                "username": "testuser",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/v1/auth/token",
            data={
                "username": "nonexistent",
                "password": "somepassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
```

### Example: User Endpoint Tests

```python
# tests/test_users.py
import pytest
from fastapi import status

class TestUserEndpoints:

    def test_create_user_success(self, client):
        """Test creating a new user"""
        response = client.post(
            "/v1/users",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepass123"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data

    def test_create_user_duplicate_username(self, client, test_user):
        """Test creating user with duplicate username"""
        response = client.post(
            "/v1/users",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_get_user_by_id_success(self, client, test_user, auth_headers):
        """Test getting user by ID"""
        response = client.get(
            f"/v1/users/{test_user.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username

    def test_get_user_unauthorized(self, client, test_user):
        """Test getting user without authentication"""
        response = client.get(f"/v1/users/{test_user.id}")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_user_success(self, client, test_user, auth_headers):
        """Test updating user"""
        response = client.put(
            f"/v1/users/{test_user.id}",
            headers=auth_headers,
            json={"email": "updated@example.com"}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "updated@example.com"

    def test_delete_user_success(self, client, test_user, auth_headers):
        """Test deleting user"""
        response = client.delete(
            f"/v1/users/{test_user.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
```

### Example: Item Tests

```python
# tests/test_items.py
import pytest
from fastapi import status
from decimal import Decimal

@pytest.fixture
def test_category(db):
    """Create a test category"""
    from app.db.models.Categorys.main import Category
    category = Category(name="Electronics", description="Electronic items")
    db.add(category)
    db.commit()
    db.refresh(category)
    return category

@pytest.fixture
def test_item(db, test_user, test_category):
    """Create a test item"""
    from app.db.models.items.item import Item
    item = Item(
        name="Test Product",
        description="Test description",
        price=Decimal("99.99"),
        category_id=test_category.id,
        user_id=test_user.id,
        stock_quantity=10
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

class TestItemEndpoints:

    def test_get_all_items(self, client, test_item, auth_headers):
        """Test getting all items"""
        response = client.get("/v1/items", headers=auth_headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) > 0
        assert data[0]["id"] == test_item.id

    def test_create_item_success(self, client, test_category, auth_headers):
        """Test creating a new item"""
        response = client.post(
            "/v1/items",
            headers=auth_headers,
            json={
                "name": "New Product",
                "description": "New description",
                "price": 149.99,
                "category_id": test_category.id,
                "stock_quantity": 5
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Product"
        assert data["price"] == 149.99

    def test_get_item_by_id(self, client, test_item, auth_headers):
        """Test getting item by ID"""
        response = client.get(
            f"/v1/items/{test_item.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_item.id
        assert data["name"] == test_item.name

    def test_update_item(self, client, test_item, auth_headers):
        """Test updating an item"""
        response = client.put(
            f"/v1/items/{test_item.id}",
            headers=auth_headers,
            json={"price": 79.99}
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["price"] == 79.99

    def test_delete_item(self, client, test_item, auth_headers):
        """Test deleting an item"""
        response = client.delete(
            f"/v1/items/{test_item.id}",
            headers=auth_headers
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
```

---

## 📊 Test Coverage

### Generate Coverage Report

```bash
# Terminal output
pytest --cov=app

# HTML report
pytest --cov=app --cov-report=html

# Open HTML report
# Windows
start htmlcov/index.html

# macOS
open htmlcov/index.html

# Linux
xdg-open htmlcov/index.html
```

### Coverage Goals

- **Target**: 80%+ coverage
- **Critical paths**: 95%+ (auth, transactions)
- **Models**: 70%+
- **Routers**: 85%+

---

## 🎯 Best Practices

### 1. Test Naming

```python
def test_<action>_<expected_result>():
    # Good: test_create_user_success
    # Good: test_login_invalid_credentials
    # Bad: test_user_1
```

### 2. Arrange-Act-Assert Pattern

```python
def test_example():
    # Arrange: Set up test data
    user_data = {"username": "test", "password": "pass"}

    # Act: Perform the action
    response = client.post("/users", json=user_data)

    # Assert: Check the results
    assert response.status_code == 201
```

### 3. Use Fixtures for Common Setup

```python
@pytest.fixture
def common_test_data():
    return {"key": "value"}

def test_with_fixture(common_test_data):
    assert common_test_data["key"] == "value"
```

### 4. Test Edge Cases

- Empty inputs
- Invalid data types
- Boundary values
- Missing required fields
- Unauthorized access

### 5. Isolate Tests

- Each test should be independent
- Use database transactions
- Clean up after tests

---

## 🐛 Debugging Tests

### Run Tests in Debug Mode

```bash
pytest -vv --pdb
```

### Print Debug Information

```python
def test_example(client):
    response = client.get("/endpoint")
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")
    assert response.status_code == 200
```

### Use pytest Markers

```python
@pytest.mark.slow
def test_slow_operation():
    pass

# Run only slow tests
# pytest -m slow
```

---

## 🔗 Related Documentation

- [API Documentation](./API_DOCUMENTATION.md)
- [Development Guide](../README.md)
- [Architecture Guide](./ARCHITECTURE.md)

---

> Last Updated: October 11, 2025
