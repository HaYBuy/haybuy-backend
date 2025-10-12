"""
Unit tests for user endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.Users.User import User


class TestGetUsers:
    """Test suite for GET /v1/user/ endpoint"""

    def test_get_all_users_empty_database(self, client: TestClient):
        """
        Test: ดึงข้อมูล users ทั้งหมดเมื่อยังไม่มี user
        Expected: ได้รับ list ว่าง
        """
        response = client.get("/v1/user/")

        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_users_with_data(
        self, client: TestClient, multiple_test_users: list[User]
    ):
        """
        Test: ดึงข้อมูล users ทั้งหมดเมื่อมี users ในระบบ
        Expected: ได้รับ list ของ users ทั้งหมด
        """
        response = client.get("/v1/user/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 5

        # ตรวจสอบว่ามี field ที่จำเป็น
        for user in data:
            assert "id" in user
            assert "username" in user
            assert "email" in user
            assert "full_name" in user
            assert "is_active" in user
            assert "created_at" in user

    def test_get_all_users_excludes_deleted(
        self, client: TestClient, db_session: Session, test_user: User
    ):
        """
        Test: ดึงข้อมูล users ต้องไม่แสดง users ที่ถูกลบ (deleted_at != None)
        Expected: ไม่มี users ที่ถูกลบในผลลัพธ์
        """
        from datetime import datetime, timezone

        # ทำเครื่องหมาย user เป็นลบ
        test_user.deleted_at = datetime.now(timezone.utc)
        db_session.commit()

        response = client.get("/v1/user/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0


class TestGetUserById:
    """Test suite for GET /v1/user/{user_id} endpoint"""

    def test_get_user_by_id_success(self, client: TestClient, test_user: User):
        """
        Test: ดึงข้อมูล user ด้วย ID ที่มีอยู่
        Expected: ได้รับข้อมูล user ที่ถูกต้อง
        """
        response = client.get(f"/v1/user/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_user.id
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["full_name"] == test_user.full_name

    def test_get_user_by_id_not_found(self, client: TestClient):
        """
        Test: ดึงข้อมูล user ด้วย ID ที่ไม่มีในระบบ
        Expected: ได้รับ status 404 และ error message
        """
        response = client.get("/v1/user/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "User not found"

    def test_get_user_by_invalid_id_type(self, client: TestClient):
        """
        Test: ดึงข้อมูล user ด้วย ID ที่ไม่ใช่ตัวเลข
        Expected: ได้รับ status 422 (Validation Error)
        """
        response = client.get("/v1/user/invalid_id")

        assert response.status_code == 422


class TestUpdateUser:
    """Test suite for PUT /v1/user/me endpoint"""

    def test_update_user_success(
        self, authenticated_client: TestClient, test_user: User, db_session: Session
    ):
        """
        Test: อัพเดทข้อมูล user ของตัวเองสำเร็จ
        Expected: ข้อมูล user ถูกอัพเดท
        """
        new_data = {
            "username": test_user.username,
            "full_name": "Updated Full Name",
            "email": test_user.email,
            "password": "newpassword123",
        }

        response = authenticated_client.put("/v1/user/me", json=new_data)

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Full Name"
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email

        # Verify password was updated in database
        db_session.refresh(test_user)
        import bcrypt

        assert bcrypt.checkpw(
            "newpassword123".encode("utf-8"), test_user.password.encode("utf-8")
        )

    def test_update_user_without_authentication(self, client: TestClient):
        """
        Test: อัพเดทข้อมูล user โดยไม่มี authentication
        Expected: ได้รับ status 401 (Unauthorized)
        """
        response = client.put(
            "/v1/user/me",
            json={
                "username": "test",
                "full_name": "Test",
                "email": "test@test.com",
                "password": "test123",
            },
        )

        assert response.status_code == 401

    def test_update_user_with_invalid_token(self, client: TestClient):
        """
        Test: อัพเดทข้อมูล user ด้วย invalid token
        Expected: ได้รับ status 401 (Unauthorized)
        """
        client.headers = {"Authorization": "Bearer invalid_token"}

        response = client.put(
            "/v1/user/me",
            json={
                "username": "test",
                "full_name": "Test",
                "email": "test@test.com",
                "password": "test123",
            },
        )

        assert response.status_code == 401

    def test_update_user_with_missing_fields(self, authenticated_client: TestClient):
        """
        Test: อัพเดทข้อมูล user โดยขาด required fields
        Expected: ได้รับ status 422 (Validation Error)
        """
        response = authenticated_client.put(
            "/v1/user/me",
            json={
                "full_name": "Test",
            },
        )

        assert response.status_code == 422


class TestDeleteUser:
    """Test suite for DELETE /v1/user/me endpoint"""

    def test_delete_user_success(
        self, authenticated_client: TestClient, test_user: User, db_session: Session
    ):
        """
        Test: ลบ user ของตัวเอง (soft delete)
        Expected: user ถูก soft delete (deleted_at มีค่า)
        """
        response = authenticated_client.delete("/v1/user/me")

        # ตรวจสอบว่า endpoint ทำงานสำเร็จ
        assert response.status_code in [200, 204]

        # ตรวจสอบว่า user ถูก soft delete
        db_session.refresh(test_user)
        assert test_user.deleted_at is not None

    def test_delete_user_without_authentication(self, client: TestClient):
        """
        Test: ลบ user โดยไม่มี authentication
        Expected: ได้รับ status 401 (Unauthorized)
        """
        response = client.delete("/v1/user/me")

        assert response.status_code == 401

    def test_delete_user_with_invalid_token(self, client: TestClient):
        """
        Test: ลบ user ด้วย invalid token
        Expected: ได้รับ status 401 (Unauthorized)
        """
        client.headers = {"Authorization": "Bearer invalid_token"}

        response = client.delete("/v1/user/me")

        assert response.status_code == 401

    def test_deleted_user_not_in_user_list(
        self, authenticated_client: TestClient, test_user: User, client: TestClient
    ):
        """
        Test: user ที่ถูกลบแล้วต้องไม่ปรากฏใน GET /v1/user/
        Expected: ไม่พบ user ที่ถูกลบใน list
        """
        # ลบ user
        authenticated_client.delete("/v1/user/me")

        # ดึง list users
        response = client.get("/v1/user/")

        assert response.status_code == 200
        data = response.json()
        user_ids = [user["id"] for user in data]
        assert test_user.id not in user_ids


class TestUserDataValidation:
    """Test suite for user data validation"""

    def test_update_user_with_invalid_email(
        self, authenticated_client: TestClient, test_user: User
    ):
        """
        Test: อัพเดทข้อมูล user ด้วย email format ที่ไม่ถูกต้อง
        Expected: ได้รับ status 422 (Validation Error)
        """
        response = authenticated_client.put(
            "/v1/user/me",
            json={
                "username": test_user.username,
                "full_name": "Test User",
                "email": "invalid-email-format",
                "password": "password123",
            },
        )

        assert response.status_code == 422

    def test_update_user_with_empty_password(
        self, authenticated_client: TestClient, test_user: User
    ):
        """
        Test: อัพเดทข้อมูล user ด้วย password ที่ว่างเปล่า
        Expected: ได้รับ status 422 (Validation Error)
        """
        response = authenticated_client.put(
            "/v1/user/me",
            json={
                "username": test_user.username,
                "full_name": "Test User",
                "email": test_user.email,
                "password": "",
            },
        )

        assert response.status_code == 422
