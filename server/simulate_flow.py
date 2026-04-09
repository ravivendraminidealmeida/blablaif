from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal
from app.models import models

def test_flow():
    # Setup - seed college
    db = SessionLocal()
    try:
        college = db.query(models.College).filter(models.College.id == 1).first()
        if not college:
            college = models.College(id=1, name="IFSP Sao Paulo", address="Rua Pedro Vicente")
            db.add(college)
            db.commit()
    finally:
        db.close()

    client = TestClient(app)

    # 1. Register student
    register_data = {
        "name": "Jane Doe",
        "email": "jane@ifsp.edu.br",
        "phone": "123456789",
        "role": "Student",
        "college_id": 1,
        "password": "secretpassword"
    }
    print("Testing Registration...")
    resp = client.post("/api/v1/auth/register", json=register_data)
    if resp.status_code == 400 and "already exists" in resp.text:
       print("User already exists, continuing...")
    else:
       print("Register Response:", resp.status_code, resp.json())
       assert resp.status_code == 200, f"Register failed: {resp.text}"

    # 2. Login
    print("Testing Login...")
    login_data = {
        "username": "jane@ifsp.edu.br",
        "password": "secretpassword"
    }
    resp = client.post("/api/v1/auth/login", data=login_data) # OAuth2 uses form data
    print("Login Response:", resp.status_code, resp.json())
    assert resp.status_code == 200, f"Login failed: {resp.text}"
    token = resp.json()["access_token"]

    # 3. Access protected route
    print("Testing Protected Route...")
    headers = {"Authorization": f"Bearer {token}"}
    resp = client.get("/", headers=headers)
    print("Protected Route Response:", resp.status_code, resp.json())
    assert resp.status_code == 200, f"Protected route failed: {resp.text}"
    print("Flow completed successfully!")

if __name__ == "__main__":
    test_flow()
