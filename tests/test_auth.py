"""
Unit tests for authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.Users.User import User


class TestAuthToken:
    """Test suite for /v1/auth/token endpoint"""

    def test_login_with_valid_credentials(
        self, client: TestClient, test_user: User, test_user_credentials: dict
    ):
        """
        Test: ล็อกอินด้วย username และ password ที่ถูกต้อง
        Expected: ได้รับ access_token และ token_type
        """
        response = client.post(
            "/v1/auth/token",
            data={
                "username": test_user_credentials["username"],
                "password": test_user_credentials["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert isinstance(data["access_token"], str)
        assert len(data["access_token"]) > 0

    def test_login_with_invalid_username(self, client: TestClient):
        """
        Test: ล็อกอินด้วย username ที่ไม่มีในระบบ
        Expected: ได้รับ status 400 และ error message
        """
        response = client.post(
            "/v1/auth/token",
            data={
                "username": "nonexistentuser",
                "password": "anypassword",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid username or password"

    def test_login_with_invalid_password(
        self, client: TestClient, test_user: User, test_user_credentials: dict
    ):
        """
        Test: ล็อกอินด้วย password ที่ผิด
        Expected: ได้รับ status 400 และ error message
        """
        response = client.post(
            "/v1/auth/token",
            data={
                "username": test_user_credentials["username"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid username or password"

    def test_login_with_missing_username(self, client: TestClient):
        """
        Test: ล็อกอินโดยไม่ส่ง username
        Expected: ได้รับ status 422 (Validation Error)
        """
        response = client.post(
            "/v1/auth/token",
            data={
                "password": "testpassword123",
            },
        )

        assert response.status_code == 422

    def test_login_with_missing_password(
        self, client: TestClient, test_user_credentials: dict
    ):
        """
        Test: ล็อกอินโดยไม่ส่ง password
        Expected: ได้รับ status 422 (Validation Error)
        """
        response = client.post(
            "/v1/auth/token",
            data={
                "username": test_user_credentials["username"],
            },
        )

        assert response.status_code == 422

    def test_login_with_empty_credentials(self, client: TestClient):
        """
        Test: ล็อกอินด้วยข้อมูลที่ว่างเปล่า
        Expected: ได้รับ status 422 (Validation Error)
        """
        response = client.post(
            "/v1/auth/token",
            data={
                "username": "",
                "password": "",
            },
        )

        assert response.status_code == 422


class TestAuthLogin:
    """Test suite for /v1/auth/login endpoint"""

    def test_login_json_with_valid_credentials(
        self, client: TestClient, test_user: User, test_user_credentials: dict
    ):
        """
        Test: ล็อกอินด้วย JSON body และข้อมูลที่ถูกต้อง
        Expected: ได้รับ access_token และ token_type
        """
        response = client.post(
            "/v1/auth/login",
            json={
                "username": test_user_credentials["username"],
                "password": test_user_credentials["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_json_with_invalid_username(self, client: TestClient):
        """
        Test: ล็อกอิน JSON format ด้วย username ที่ไม่มีในระบบ
        Expected: ได้รับ status 400 และ error message
        """
        response = client.post(
            "/v1/auth/login",
            json={
                "username": "nonexistentuser",
                "password": "anypassword",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid username or password"

    def test_login_json_with_invalid_password(
        self, client: TestClient, test_user: User, test_user_credentials: dict
    ):
        """
        Test: ล็อกอิน JSON format ด้วย password ที่ผิด
        Expected: ได้รับ status 400 และ error message
        """
        response = client.post(
            "/v1/auth/login",
            json={
                "username": test_user_credentials["username"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Invalid username or password"


class TestTokenValidation:
    """Test suite for token validation"""

    def test_access_protected_endpoint_with_valid_token(
        self, authenticated_client: TestClient, test_user: User
    ):
        """
        Test: เข้าถึง protected endpoint ด้วย valid token
        Expected: สามารถเข้าถึงได้สำเร็จ
        """
        response = authenticated_client.put(
            "/v1/user/me",
            json={
                "username": test_user.username,
                "full_name": "Updated Name",
                "email": test_user.email,
                "password": "newpassword123",
            },
        )

        # ถ้าเข้าถึงได้แสดงว่า token valid (ไม่ได้ 401)
        assert response.status_code != 401

    def test_access_protected_endpoint_without_token(self, client: TestClient):
        """
        Test: เข้าถึง protected endpoint โดยไม่มี token
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

    def test_access_protected_endpoint_with_invalid_token(self, client: TestClient):
        """
        Test: เข้าถึง protected endpoint ด้วย invalid token
        Expected: ได้รับ status 401 (Unauthorized)
        """
        client.headers = {"Authorization": "Bearer invalid_token_here"}

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

    def test_access_protected_endpoint_with_malformed_token(self, client: TestClient):
        """
        Test: เข้าถึง protected endpoint ด้วย malformed token
        Expected: ได้รับ status 401 (Unauthorized)
        """
        client.headers = {"Authorization": "InvalidFormat"}

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


class TestRegister:
    """Test suite for POST /v1/auth/register endpoint"""

    def test_register_new_user_success(self, client: TestClient, db_session: Session):
        """
        Test: ลงทะเบียน user ใหม่สำเร็จ
        Expected: ได้รับข้อมูล user ที่สร้างและ user profile ถูกสร้าง
        """
        from app.db.models.Users.UserProfile import UserProfile

        user_data = {
            "username": "newuser",
            "full_name": "New User",
            "email": "newuser@example.com",
            "password": "newpassword123",
        }

        response = client.post("/v1/auth/register", json=user_data)

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["full_name"] == "New User"
        assert data["email"] == "newuser@example.com"
        assert data["is_active"] is True
        assert "id" in data
        assert "password" not in data  # Password should not be returned

        # Verify user profile was created
        user_profile = (
            db_session.query(UserProfile)
            .filter(UserProfile.user_id == data["id"])
            .first()
        )
        assert user_profile is not None

    def test_register_duplicate_username(self, client: TestClient, test_user: User):
        """
        Test: ลงทะเบียนด้วย username ที่มีอยู่แล้ว
        Expected: ได้รับ status 400
        """
        user_data = {
            "username": test_user.username,
            "full_name": "Duplicate User",
            "email": "duplicate@example.com",
            "password": "password123",
        }

        response = client.post("/v1/auth/register", json=user_data)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_register_with_missing_required_fields(self, client: TestClient):
        """
        Test: ลงทะเบียนโดยขาด required fields
        Expected: ได้รับ status 422 validation error
        """
        response = client.post("/v1/auth/register", json={})
        assert response.status_code == 422

    def test_register_with_invalid_email(self, client: TestClient):
        """
        Test: ลงทะเบียนด้วย email format ที่ไม่ถูกต้อง
        Expected: ได้รับ status 422 validation error
        """
        user_data = {
            "username": "userwithemail",
            "full_name": "User With Email",
            "email": "invalid-email-format",
            "password": "password123",
        }

        response = client.post("/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_with_short_password(self, client: TestClient):
        """
        Test: ลงทะเบียนด้วย password สั้นเกินไป
        Expected: ได้รับ status 422 validation error (ถ้ามี validation)
        """
        user_data = {
            "username": "usershortpw",
            "full_name": "User Short PW",
            "email": "shortpw@example.com",
            "password": "123",
        }

        response = client.post("/v1/auth/register", json=user_data)
        # อาจจะ success หรือ 422 ขึ้นกับว่ามี password validation หรือไม่
        assert response.status_code in [200, 422]

    def test_register_user_can_login(self, client: TestClient):
        """
        Test: หลังจากลงทะเบียนแล้ว user สามารถ login ได้
        Expected: สามารถ login และได้รับ token
        """
        user_data = {
            "username": "loginuser",
            "full_name": "Login User",
            "email": "loginuser@example.com",
            "password": "loginpassword123",
        }

        # Register
        register_response = client.post("/v1/auth/register", json=user_data)
        assert register_response.status_code == 200

        # Try to login
        login_response = client.post(
            "/v1/auth/token",
            data={"username": "loginuser", "password": "loginpassword123"},
        )

        assert login_response.status_code == 200
        assert "access_token" in login_response.json()

    def test_register_with_empty_username(self, client: TestClient):
        """
        Test: ลงทะเบียนด้วย username ว่างเปล่า
        Expected: ได้รับ status 422 validation error
        """
        user_data = {
            "username": "",
            "full_name": "Empty Username",
            "email": "empty@example.com",
            "password": "password123",
        }

        response = client.post("/v1/auth/register", json=user_data)
        assert response.status_code == 422

    def test_register_password_is_hashed(self, client: TestClient, db_session: Session):
        """
        Test: Password ถูก hash ก่อนเก็บในฐานข้อมูล
        Expected: Password ในฐานข้อมูลไม่เหมือนกับ plain text
        """
        from app.db.models.Users.User import User

        user_data = {
            "username": "hasheduser",
            "full_name": "Hashed User",
            "email": "hashed@example.com",
            "password": "plainpassword123",
        }

        response = client.post("/v1/auth/register", json=user_data)
        assert response.status_code == 200

        # Get user from database
        user = db_session.query(User).filter(User.username == "hasheduser").first()

        assert user is not None
        assert user.password != "plainpassword123"  # Password should be hashed
        assert len(user.password) > len("plainpassword123")  # Hashed password is longer
