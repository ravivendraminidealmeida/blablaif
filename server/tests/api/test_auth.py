import pytest

def test_register_user(client, setup_college):
    response = client.post("/api/v1/auth/register", json={
        "name": "Test User",
        "email": "test@ifsp.edu.br",
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@ifsp.edu.br"
    assert "id" in data

def test_register_duplicate_user(client, setup_college):
    user_payload = {
        "name": "Test User",
        "email": "duplicate@ifsp.edu.br",
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

def test_login_user(client, setup_college):
    # Setup - Register a user first
    client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": "login@ifsp.edu.br",
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    })

    # Test Login
    response = client.post("/api/v1/auth/login", data={
        "username": "login@ifsp.edu.br",
        "password": "securepassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, setup_college):
    client.post("/api/v1/auth/register", json={
        "name": "Login User",
        "email": "login2@ifsp.edu.br",
        "phone": "999999999",
        "role": "Student",
        "college_id": 1,
        "password": "securepassword123"
    })

    response = client.post("/api/v1/auth/login", data={
        "username": "login2@ifsp.edu.br",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_protected_route_unauthorized(client):
    response = client.get("/")
    assert response.status_code == 401

def test_protected_route_authorized(client, setup_college):
    client.post("/api/v1/auth/register", json={
        "name": "Auth User",
        "email": "auth@ifsp.edu.br",
        "phone": "999",
        "role": "Student",
        "college_id": 1,
        "password": "pass"
    })
    
    login_req = client.post("/api/v1/auth/login", data={
        "username": "auth@ifsp.edu.br",
        "password": "pass"
    })
    token = login_req.json()["access_token"]
    
    response = client.get("/", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]
    assert "Auth User" in response.json()["message"]
