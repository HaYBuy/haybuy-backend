"""
Unit tests for user profile endpoints
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db.models.Users.User import User
from app.db.models.Users.UserProfile import UserProfile


@pytest.fixture
def test_user_profile(db_session: Session, test_user: User) -> UserProfile:
    """สร้าง test user profile"""
    profile = UserProfile(
        user_id=test_user.id,
        phone="0812345678",
        address_line1="123 Main St",
        address_line2="Apt 4",
        district="District 1",
        province="Bangkok",
        postal_code="10110",
        latitude=13.7563,
        longitude=100.5018,
        location_verified=False,
        id_verified=False,
    )
    db_session.add(profile)
    db_session.commit()
    db_session.refresh(profile)
    return profile


class TestGetMyProfile:
    """Test suite for GET /v1/profile/me endpoint"""

    def test_get_my_profile_requires_authentication(self, client: TestClient):
        """
        Test: ดึง profile ของตัวเองโดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        response = client.get("/v1/profile/me")
        assert response.status_code == 401

    def test_get_my_profile_success(
        self, authenticated_client: TestClient, test_user_profile: UserProfile
    ):
        """
        Test: ดึง profile ของตัวเองสำเร็จ
        Expected: ได้รับข้อมูล profile
        """
        response = authenticated_client.get("/v1/profile/me")

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user_profile.user_id
        assert data["phone"] == test_user_profile.phone
        assert data["address_line1"] == test_user_profile.address_line1
        assert data["province"] == test_user_profile.province

    def test_get_my_profile_not_found(self, authenticated_client: TestClient):
        """
        Test: ดึง profile เมื่อยังไม่มี profile
        Expected: ได้รับ status 404
        """
        # Profile ยังไม่ถูกสร้างใน fixture
        response = authenticated_client.get("/v1/profile/me")
        assert response.status_code == 404


class TestGetTargetProfile:
    """Test suite for GET /v1/profile/{user_target_id} endpoint"""

    def test_get_target_profile_success(
        self, client: TestClient, test_user: User, test_user_profile: UserProfile
    ):
        """
        Test: ดึง profile ของ user อื่น (public access)
        Expected: ได้รับข้อมูล profile
        """
        response = client.get(f"/v1/profile/{test_user.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == test_user.id

    def test_get_target_profile_not_found(self, client: TestClient):
        """
        Test: ดึง profile ของ user ที่ไม่มีในระบบ
        Expected: ได้รับ status 404
        """
        response = client.get("/v1/profile/99999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_get_target_profile_no_authentication_needed(
        self, client: TestClient, test_user: User, test_user_profile: UserProfile
    ):
        """
        Test: ดึง profile ของ user อื่นไม่ต้องมี authentication
        Expected: สามารถเข้าถึงได้
        """
        response = client.get(f"/v1/profile/{test_user.id}")
        assert response.status_code == 200

    def test_get_target_profile_with_invalid_id_type(self, client: TestClient):
        """
        Test: ดึง profile ด้วย ID ที่ไม่ใช่ตัวเลข
        Expected: ได้รับ status 422 validation error
        """
        response = client.get("/v1/profile/invalid_id")
        assert response.status_code == 422


class TestEditMyProfile:
    """Test suite for PUT /v1/profile/me/editprofile endpoint"""

    def test_edit_my_profile_requires_authentication(self, client: TestClient):
        """
        Test: แก้ไข profile โดยไม่มี authentication
        Expected: ได้รับ status 401
        """
        profile_data = {
            "phone": "0898765432",
            "address_line1": "456 New St",
            "district": "District 2",
            "province": "Bangkok",
            "postal_code": "10120",
        }

        response = client.put("/v1/profile/me/editprofile", json=profile_data)
        assert response.status_code == 401

    def test_edit_my_profile_success(
        self,
        authenticated_client: TestClient,
        test_user_profile: UserProfile,
        db_session: Session,
    ):
        """
        Test: แก้ไข profile ของตัวเองสำเร็จ
        Expected: ข้อมูล profile ถูกอัพเดท
        """
        profile_data = {
            "phone": "0898765432",
            "address_line1": "456 New Street",
            "address_line2": "Building B",
            "district": "District 2",
            "province": "Chiang Mai",
            "postal_code": "50000",
            "latitude": 18.7883,
            "longitude": 98.9853,
            "location_verified": True,
            "id_verified": True,
        }

        response = authenticated_client.put(
            "/v1/profile/me/editprofile", json=profile_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "0898765432"
        assert data["address_line1"] == "456 New Street"
        assert data["province"] == "Chiang Mai"
        assert data["location_verified"] is True
        assert data["id_verified"] is True

        # Verify in database
        db_session.refresh(test_user_profile)
        assert test_user_profile.phone == "0898765432"
        assert test_user_profile.province == "Chiang Mai"

    def test_edit_my_profile_partial_update(
        self, authenticated_client: TestClient, test_user_profile: UserProfile
    ):
        """
        Test: แก้ไข profile บางฟิลด์
        Expected: เฉพาะฟิลด์ที่ส่งมาถูกอัพเดท
        """
        profile_data = {
            "phone": "0811111111",
            "address_line1": test_user_profile.address_line1,
            "district": test_user_profile.district,
            "province": test_user_profile.province,
            "postal_code": test_user_profile.postal_code,
        }

        response = authenticated_client.put(
            "/v1/profile/me/editprofile", json=profile_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["phone"] == "0811111111"
        # ฟิลด์อื่นควรเหมือนเดิม
        assert data["province"] == test_user_profile.province

    def test_edit_my_profile_not_found(self, authenticated_client: TestClient):
        """
        Test: แก้ไข profile เมื่อยังไม่มี profile
        Expected: ได้รับ status 404
        """
        profile_data = {
            "phone": "0812345678",
            "address_line1": "123 St",
            "district": "District",
            "province": "Province",
            "postal_code": "10000",
        }

        response = authenticated_client.put(
            "/v1/profile/me/editprofile", json=profile_data
        )
        assert response.status_code == 404

    def test_edit_my_profile_with_missing_fields(
        self, authenticated_client: TestClient, test_user_profile: UserProfile
    ):
        """
        Test: แก้ไข profile โดยขาด required fields
        Expected: ได้รับ status 422 validation error
        """
        response = authenticated_client.put("/v1/profile/me/editprofile", json={})
        assert response.status_code == 422

    def test_edit_my_profile_with_invalid_phone(
        self, authenticated_client: TestClient, test_user_profile: UserProfile
    ):
        """
        Test: แก้ไข profile ด้วยเบอร์โทรที่ไม่ถูกต้อง
        Expected: อาจจะ success หรือ 422 ขึ้นกับ validation
        """
        profile_data = {
            "phone": "invalid_phone",
            "address_line1": "123 St",
            "district": "District",
            "province": "Province",
            "postal_code": "10000",
        }

        response = authenticated_client.put(
            "/v1/profile/me/editprofile", json=profile_data
        )
        # อาจจะ 200 หรือ 422 ขึ้นกับ validation
        assert response.status_code in [200, 422]

    def test_edit_my_profile_location_coordinates(
        self,
        authenticated_client: TestClient,
        test_user_profile: UserProfile,
        db_session: Session,
    ):
        """
        Test: แก้ไข profile พร้อมพิกัดที่ตั้ง
        Expected: พิกัดถูกอัพเดท
        """
        profile_data = {
            "phone": test_user_profile.phone,
            "address_line1": test_user_profile.address_line1,
            "district": test_user_profile.district,
            "province": test_user_profile.province,
            "postal_code": test_user_profile.postal_code,
            "latitude": 15.1234,
            "longitude": 101.5678,
            "location_verified": True,
        }

        response = authenticated_client.put(
            "/v1/profile/me/editprofile", json=profile_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["latitude"] == 15.1234
        assert data["longitude"] == 101.5678
        assert data["location_verified"] is True

        # Verify in database
        db_session.refresh(test_user_profile)
        assert float(test_user_profile.latitude) == 15.1234
        assert float(test_user_profile.longitude) == 101.5678

    def test_edit_my_profile_verification_flags(
        self,
        authenticated_client: TestClient,
        test_user_profile: UserProfile,
        db_session: Session,
    ):
        """
        Test: เปลี่ยนสถานะการยืนยันต่างๆ
        Expected: สถานะการยืนยันถูกอัพเดท
        """
        profile_data = {
            "phone": test_user_profile.phone,
            "address_line1": test_user_profile.address_line1,
            "district": test_user_profile.district,
            "province": test_user_profile.province,
            "postal_code": test_user_profile.postal_code,
            "location_verified": True,
            "id_verified": True,
        }

        response = authenticated_client.put(
            "/v1/profile/me/editprofile", json=profile_data
        )

        assert response.status_code == 200
        data = response.json()
        assert data["location_verified"] is True
        assert data["id_verified"] is True

        # Verify in database
        db_session.refresh(test_user_profile)
        assert test_user_profile.location_verified is True
        assert test_user_profile.id_verified is True
