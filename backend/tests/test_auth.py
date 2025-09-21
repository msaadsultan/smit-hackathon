import pytest
from fastapi.testclient import TestClient
from backend.auth.models import UserRole, UserCreate

def test_login_success(client: TestClient, test_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user):
    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401

def test_get_me(client: TestClient, test_user):
    # First login to get token
    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    token = response.json()["access_token"]
    
    # Test /me endpoint
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["email"] == test_user.email
    assert response.json()["role"] == test_user.role

def test_register_user(client: TestClient, test_user):
    # First login as admin
    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    token = response.json()["access_token"]
    
    # Register new user
    new_user = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "role": UserRole.STAFF
    }
    response = client.post(
        "/auth/register",
        headers={"Authorization": f"Bearer {token}"},
        json=new_user
    )
    assert response.status_code == 200
    assert response.json()["email"] == new_user["email"]
    assert response.json()["role"] == new_user["role"]

def test_register_without_admin(client: TestClient):
    new_user = {
        "email": "newuser@example.com",
        "password": "newpassword",
        "role": UserRole.STAFF
    }
    response = client.post("/auth/register", json=new_user)
    assert response.status_code == 401