"""
Unit tests for category endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

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
def test_parent_category(db_session: Session) -> Category:
    """สร้าง parent category สำหรับทดสอบ hierarchy"""
    category = Category(name="Technology", slug="technology", parent_id=None)
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def test_child_category(
    db_session: Session, test_parent_category: Category
) -> Category:
    """สร้าง child category"""
    category = Category(
        name="Smartphones", slug="smartphones", parent_id=test_parent_category.id
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category


@pytest.fixture
def multiple_test_categories(db_session: Session) -> list[Category]:
    """สร้าง test categories หลายรายการ"""
    categories = []
    for i in range(1, 6):
        category = Category(name=f"Category {i}", slug=f"category-{i}", parent_id=None)
        db_session.add(category)
        categories.append(category)

    db_session.commit()
    for category in categories:
        db_session.refresh(category)

    return categories


class TestCreateCategory:
    """Test suite for POST /v1/category/ endpoint"""

    def test_create_category_success(self, client: TestClient):
        """
        Test: สร้าง category ใหม่สำเร็จ
        Expected: ได้รับ category ที่สร้างพร้อม id
        """
        category_data = {"name": "Books", "slug": "books", "parent_id": None}

        response = client.post("/v1/category/", json=category_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Books"
        assert data["slug"] == "books"
        assert data["parent_id"] is None
        assert "id" in data
        assert "created_at" in data

    def test_create_category_with_parent(
        self, client: TestClient, test_parent_category: Category
    ):
        """
        Test: สร้าง category ที่มี parent category
        Expected: สร้างสำเร็จและมี parent_id
        """
        category_data = {
            "name": "Laptops",
            "slug": "laptops",
            "parent_id": test_parent_category.id,
        }

        response = client.post("/v1/category/", json=category_data)

        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == test_parent_category.id

    def test_create_category_duplicate_name(
        self, client: TestClient, test_category: Category
    ):
        """
        Test: สร้าง category ด้วยชื่อที่มีอยู่แล้ว
        Expected: ได้รับ status 409 conflict
        """
        category_data = {
            "name": test_category.name,
            "slug": "electronics-2",
            "parent_id": None,
        }

        response = client.post("/v1/category/", json=category_data)

        assert response.status_code == 409
        assert response.json()["detail"] == "Category name already exists"

    def test_create_category_with_nonexistent_parent(self, client: TestClient):
        """
        Test: สร้าง category ด้วย parent_id ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        category_data = {
            "name": "New Category",
            "slug": "new-category",
            "parent_id": 99999,
        }

        response = client.post("/v1/category/", json=category_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Parent category not found"

    def test_create_category_with_invalid_slug(self, client: TestClient):
        """
        Test: สร้าง category ด้วย slug format ที่ไม่ถูกต้อง
        Expected: ได้รับ status 422 validation error
        """
        category_data = {
            "name": "Invalid Slug",
            "slug": "Invalid Slug!",  # มีตัวพิมพ์ใหญ่และอักขระพิเศษ
            "parent_id": None,
        }

        response = client.post("/v1/category/", json=category_data)

        assert response.status_code == 422

    def test_create_category_with_missing_required_fields(self, client: TestClient):
        """
        Test: สร้าง category โดยขาด required fields
        Expected: ได้รับ status 422 validation error
        """
        response = client.post("/v1/category/", json={})

        assert response.status_code == 422

    def test_create_category_with_short_name(self, client: TestClient):
        """
        Test: สร้าง category ด้วยชื่อสั้นเกินไป
        Expected: ได้รับ status 422 validation error
        """
        category_data = {
            "name": "A",  # สั้นเกินไป (min 2 chars)
            "slug": "a",
            "parent_id": None,
        }

        response = client.post("/v1/category/", json=category_data)

        assert response.status_code == 422


class TestListCategories:
    """Test suite for GET /v1/category/ endpoint"""

    def test_list_categories_empty(self, client: TestClient):
        """
        Test: ดึง list categories เมื่อยังไม่มีข้อมูล
        Expected: ได้รับ list ว่าง
        """
        response = client.get("/v1/category/")

        assert response.status_code == 200
        assert response.json() == []

    def test_list_categories_with_data(
        self, client: TestClient, multiple_test_categories: list[Category]
    ):
        """
        Test: ดึง list categories ทั้งหมด
        Expected: ได้รับ list ของ categories
        """
        response = client.get("/v1/category/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all("id" in cat for cat in data)
        assert all("name" in cat for cat in data)
        assert all("slug" in cat for cat in data)

    def test_list_categories_with_pagination(
        self, client: TestClient, multiple_test_categories: list[Category]
    ):
        """
        Test: ใช้ pagination (skip และ limit)
        Expected: ได้รับ categories ตามจำนวนที่กำหนด
        """
        response = client.get("/v1/category/?skip=0&limit=3")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

        # ทดสอบหน้าถัดไป
        response2 = client.get("/v1/category/?skip=3&limit=3")
        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2) == 2

    def test_list_categories_with_children(
        self,
        client: TestClient,
        test_parent_category: Category,
        test_child_category: Category,
    ):
        """
        Test: ดึง list categories ที่มี children
        Expected: ได้รับ categories พร้อม children array
        """
        response = client.get("/v1/category/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert all("children" in cat for cat in data)


class TestGetCategoryById:
    """Test suite for GET /v1/category/{category_id} endpoint"""

    def test_get_category_by_id_success(
        self, client: TestClient, test_category: Category
    ):
        """
        Test: ดึงข้อมูล category ด้วย ID ที่มีอยู่
        Expected: ได้รับข้อมูล category ที่ถูกต้อง
        """
        response = client.get(f"/v1/category/{test_category.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_category.id
        assert data["name"] == test_category.name
        assert data["slug"] == test_category.slug

    def test_get_category_by_id_not_found(self, client: TestClient):
        """
        Test: ดึงข้อมูล category ด้วย ID ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = client.get("/v1/category/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    def test_get_category_by_id_with_children(
        self,
        client: TestClient,
        test_parent_category: Category,
        test_child_category: Category,
    ):
        """
        Test: ดึงข้อมูล parent category ที่มี children
        Expected: ได้รับ category พร้อม children array
        """
        response = client.get(f"/v1/category/{test_parent_category.id}")

        assert response.status_code == 200
        data = response.json()
        assert "children" in data
        assert len(data["children"]) >= 1
        assert data["children"][0]["id"] == test_child_category.id

    def test_get_category_by_invalid_id_type(self, client: TestClient):
        """
        Test: ดึงข้อมูล category ด้วย ID ที่ไม่ใช่ตัวเลข
        Expected: ได้รับ status 422 validation error
        """
        response = client.get("/v1/category/invalid_id")

        assert response.status_code == 422


class TestUpdateCategory:
    """Test suite for PUT /v1/category/{category_id} endpoint"""

    def test_update_category_success(
        self, client: TestClient, test_category: Category, db_session: Session
    ):
        """
        Test: อัพเดท category สำเร็จ
        Expected: ข้อมูล category ถูกอัพเดท
        """
        update_data = {
            "name": "Updated Electronics",
            "slug": "updated-electronics",
            "parent_id": None,
        }

        response = client.put(f"/v1/category/{test_category.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Electronics"
        assert data["slug"] == "updated-electronics"

        # Verify in database
        db_session.refresh(test_category)
        assert test_category.name == "Updated Electronics"

    def test_update_category_partial(self, client: TestClient, test_category: Category):
        """
        Test: อัพเดท category บางฟิลด์
        Expected: เฉพาะฟิลด์ที่ส่งมาถูกอัพเดท
        """
        update_data = {"name": "Partially Updated"}

        response = client.put(f"/v1/category/{test_category.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Partially Updated"
        assert data["slug"] == test_category.slug  # ไม่เปลี่ยน

    def test_update_category_not_found(self, client: TestClient):
        """
        Test: อัพเดท category ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        update_data = {"name": "New Name"}

        response = client.put("/v1/category/99999", json=update_data)

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    def test_update_category_change_parent(
        self,
        client: TestClient,
        test_category: Category,
        test_parent_category: Category,
    ):
        """
        Test: เปลี่ยน parent ของ category
        Expected: parent_id ถูกอัพเดท
        """
        update_data = {"parent_id": test_parent_category.id}

        response = client.put(f"/v1/category/{test_category.id}", json=update_data)

        assert response.status_code == 200
        data = response.json()
        assert data["parent_id"] == test_parent_category.id

    def test_update_category_with_empty_body(
        self, client: TestClient, test_category: Category
    ):
        """
        Test: อัพเดท category โดยไม่ส่งข้อมูล
        Expected: ไม่มีการเปลี่ยนแปลง แต่ response success
        """
        response = client.put(f"/v1/category/{test_category.id}", json={})

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_category.name


class TestDeleteCategory:
    """Test suite for DELETE /v1/category/{category_id} endpoint"""

    def test_delete_category_success(
        self, client: TestClient, test_category: Category, db_session: Session
    ):
        """
        Test: ลบ category สำเร็จ
        Expected: category ถูกลบจากฐานข้อมูล
        """
        category_id = test_category.id

        response = client.delete(f"/v1/category/{category_id}")

        assert response.status_code == 200
        assert response.json()["detail"] == "Category deleted successfully"

        # Verify deleted from database
        deleted_category = (
            db_session.query(Category).filter(Category.id == category_id).first()
        )
        assert deleted_category is None

    def test_delete_category_not_found(self, client: TestClient):
        """
        Test: ลบ category ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = client.delete("/v1/category/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Category not found"

    def test_delete_category_with_invalid_id_type(self, client: TestClient):
        """
        Test: ลบ category ด้วย ID ที่ไม่ใช่ตัวเลข
        Expected: ได้รับ status 422 validation error
        """
        response = client.delete("/v1/category/invalid_id")

        assert response.status_code == 422

    def test_delete_parent_category_with_children(
        self,
        client: TestClient,
        test_parent_category: Category,
        test_child_category: Category,
    ):
        """
        Test: ลบ parent category ที่มี children
        Expected: สามารถลบได้ (หรือ handle cascade delete ตาม business logic)
        """
        response = client.delete(f"/v1/category/{test_parent_category.id}")

        # ขึ้นกับ business logic - อาจจะ success หรือ error
        assert response.status_code in [200, 400, 409]

    def test_cannot_get_deleted_category(
        self, client: TestClient, test_category: Category
    ):
        """
        Test: หลังจากลบแล้ว ไม่สามารถดึงข้อมูล category นั้นได้
        Expected: GET ได้รับ status 404
        """
        category_id = test_category.id

        # ลบ category
        client.delete(f"/v1/category/{category_id}")

        # พยายามดึงข้อมูล
        response = client.get(f"/v1/category/{category_id}")
        assert response.status_code == 404
