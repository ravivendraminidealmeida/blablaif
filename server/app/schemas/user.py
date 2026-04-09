from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.models import RoleType
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: RoleType = RoleType.Student
    college_id: int

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
