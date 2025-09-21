import pytest
from fastapi.testclient import TestClient
from backend.models import StudentCreate, StudentUpdate

def get_auth_headers(client: TestClient, test_user) -> dict:
    response = client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_create_student(client: TestClient, test_user):
    headers = get_auth_headers(client, test_user)
    student_data = {
        "id": "ST001",
        "name": "John Doe",
        "department": "Computer Science",
        "email": "john@example.com"
    }
    response = client.post("/students/", headers=headers, json=student_data)
    assert response.status_code == 200
    assert response.json()["name"] == student_data["name"]
    assert response.json()["department"] == student_data["department"]
    assert response.json()["email"] == student_data["email"]

def test_get_student(client: TestClient, test_user):
    # First create a student
    headers = get_auth_headers(client, test_user)
    student_data = {
        "id": "ST002",
        "name": "Jane Doe",
        "department": "Physics",
        "email": "jane@example.com"
    }
    client.post("/students/", headers=headers, json=student_data)
    
    # Now retrieve the student
    response = client.get(f"/students/{student_data['id']}", headers=headers)
    assert response.status_code == 200
    assert response.json()["name"] == student_data["name"]
    assert response.json()["department"] == student_data["department"]

def test_list_students(client: TestClient, test_user):
    headers = get_auth_headers(client, test_user)
    response = client.get("/students/", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_update_student(client: TestClient, test_user):
    # First create a student
    headers = get_auth_headers(client, test_user)
    student_data = {
        "id": "ST003",
        "name": "Alice Smith",
        "department": "Mathematics",
        "email": "alice@example.com"
    }
    client.post("/students/", headers=headers, json=student_data)
    
    # Update the student
    update_data = {
        "department": "Applied Mathematics"
    }
    response = client.put(
        f"/students/{student_data['id']}",
        headers=headers,
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["department"] == update_data["department"]
    assert response.json()["name"] == student_data["name"]

def test_delete_student(client: TestClient, test_user):
    # First create a student
    headers = get_auth_headers(client, test_user)
    student_data = {
        "id": "ST004",
        "name": "Bob Wilson",
        "department": "Chemistry",
        "email": "bob@example.com"
    }
    client.post("/students/", headers=headers, json=student_data)
    
    # Delete the student
    response = client.delete(
        f"/students/{student_data['id']}",
        headers=headers
    )
    assert response.status_code == 200
    
    # Verify deletion
    response = client.get(
        f"/students/{student_data['id']}",
        headers=headers
    )
    assert response.status_code == 404

def test_unauthorized_access(client: TestClient):
    response = client.get("/students/")
    assert response.status_code == 401