import pytest

def test_register_user(client, setup_college):
    response = client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@aluno.ifsp.edu.br",
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@aluno.ifsp.edu.br"
    assert "id" in data

def test_register_duplicate_user(client, setup_college):
    user_payload = {
        "name": "Test User",
        "email": "duplicate@aluno.ifsp.edu.br",
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    }
    # Register first time
    client.post("/api/v1/auth/register", json=user_payload)
    
    # Register second time
    response = client.post("/api/v1/auth/register", json=user_payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_register_rejects_non_student_email(client, setup_college):
    response = client.post("/api/v1/auth/register", json={
        "name": "Invalid User",
        "email": "invalid@example.com",
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    })
    assert response.status_code == 422

def test_login_user(client, setup_college):
    # Setup - Register a user first
    client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": "login@aluno.ifsp.edu.br",
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    })

    # Test Login
    response = client.post("/api/v1/auth/login", data={
        "username": "login@aluno.ifsp.edu.br",
        "password": "securepassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, setup_college):
    client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": "login2@aluno.ifsp.edu.br",
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    })

    response = client.post("/api/v1/auth/login", data={
        "username": "login2@aluno.ifsp.edu.br",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_protected_route_unauthorized(client):
    response = client.get("/")
    assert response.status_code == 401

def test_protected_route_authorized(client, setup_college):
    client.post("/api/v1/auth/register", json={
        "name": "Auth User",
        "email": "auth@aluno.ifsp.edu.br",
        "phone": "999",
        "role": "Student",
        "college_id": 1,
        "password": "pass"
    })
    
    login_req = client.post("/api/v1/auth/login", data={
        "username": "auth@aluno.ifsp.edu.br",
        "password": "pass"
    })
    token = login_req.json()["access_token"]
    
    response = client.get("/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]
    assert "Auth User" in response.json()["message"]

def test_update_profile(client, setup_college):
    client.post("/api/v1/auth/register", json={
        "name": "Profile User",
        "email": "profile@aluno.ifsp.edu.br",
        "phone": "999",
        "role": "Student",
        "college_id": 1,
        "password": "pass"
    })
    login_req = client.post("/api/v1/auth/login", data={
        "username": "profile@aluno.ifsp.edu.br",
        "password": "pass"
    })
    token = login_req.json()["access_token"]

    response = client.patch("/api/v1/auth/me", json={
        "name": "Updated Profile",
        "email": "updated.profile@aluno.ifsp.edu.br",
        "phone": "(17) 99999-1111",
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Profile"
    assert data["email"] == "updated.profile@aluno.ifsp.edu.br"
    assert data["phone"] == "(17) 99999-1111"
    assert data["role"] == "Student"
    assert data["college_id"] == 1

def test_update_profile_rejects_duplicate_email(client, setup_college):
    client.post("/api/v1/auth/register", json={
        "name": "First User",
        "email": "first@aluno.ifsp.edu.br",
        "phone": "111",
        "role": "Student",
        "college_id": 1,
        "password": "pass"
    })
    client.post("/api/v1/auth/register", json={
        "name": "Second User",
        "email": "second@aluno.ifsp.edu.br",
        "phone": "222",
        "role": "Student",
        "college_id": 1,
        "password": "pass"
    })
    login_req = client.post("/api/v1/auth/login", data={
        "username": "first@aluno.ifsp.edu.br",
        "password": "pass"
    })
    token = login_req.json()["access_token"]

    response = client.patch("/api/v1/auth/me", json={
        "email": "second@aluno.ifsp.edu.br",
    }, headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]
