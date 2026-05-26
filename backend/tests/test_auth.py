"""
Authentication endpoint tests.
"""
import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from tests.factories import UserFactory


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory(email="test@example.com", password=None)


@pytest.mark.django_db
class TestRegistration:
    def test_register_success(self, client):
        url = reverse("auth-register")
        payload = {
            "email": "newuser@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = client.post(url, payload, format="json")
        assert response.status_code == 201
        assert "access" in response.data
        assert "refresh" in response.data
        assert response.data["user"]["email"] == "newuser@example.com"

    def test_register_password_mismatch(self, client):
        url = reverse("auth-register")
        payload = {
            "email": "newuser2@example.com",
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "SecurePass123!",
            "password_confirm": "WrongPass123!",
        }
        response = client.post(url, payload, format="json")
        assert response.status_code == 400

    def test_register_duplicate_email(self, client, user):
        url = reverse("auth-register")
        payload = {
            "email": user.email,
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
        }
        response = client.post(url, payload, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestLogin:
    def test_login_success(self, client, db):
        user = UserFactory()
        user.set_password("TestPassword123!")
        user.save()

        url = reverse("auth-login")
        response = client.post(url, {"email": user.email, "password": "TestPassword123!"}, format="json")
        assert response.status_code == 200
        assert "access" in response.data

    def test_login_wrong_password(self, client, db):
        user = UserFactory()
        url = reverse("auth-login")
        response = client.post(url, {"email": user.email, "password": "wrongpassword"}, format="json")
        assert response.status_code == 400

    def test_login_inactive_user(self, client, db):
        user = UserFactory(is_active=False)
        user.set_password("TestPassword123!")
        user.save()
        url = reverse("auth-login")
        response = client.post(url, {"email": user.email, "password": "TestPassword123!"}, format="json")
        assert response.status_code == 400


@pytest.mark.django_db
class TestPasswordReset:
    def test_reset_request_always_200(self, client):
        """Should return 200 even for non-existent emails (prevent enumeration)."""
        url = reverse("password-reset-request")
        response = client.post(url, {"email": "nonexistent@example.com"}, format="json")
        assert response.status_code == 200
