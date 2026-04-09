import jwt
from app.core import security
from app.core.config import settings

def test_password_hashing():
    password = "supersecretpassword"
    hashed = security.get_password_hash(password)
    
    assert password != hashed
    assert security.verify_password(password, hashed) is True
    assert security.verify_password("wrongpassword", hashed) is False

def test_create_access_token():
    data = {"sub": "123"}
    token = security.create_access_token(data)
    
    decoded_payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded_payload["sub"] == "123"
    assert "exp" in decoded_payload
