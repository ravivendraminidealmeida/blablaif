from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict, Field, field_validator
from app.models.models import RoleType

IFSP_STUDENT_EMAIL_DOMAIN = "@aluno.ifsp.edu.br"

class UserBase(BaseModel):
    name: str = Field(min_length=1)
    email: EmailStr
    phone: str = Field(min_length=1)
    role: RoleType = RoleType.Student
    college_id: int

    @field_validator("email")
    @classmethod
    def validate_student_email(cls, email: EmailStr) -> EmailStr:
        if not str(email).lower().endswith(IFSP_STUDENT_EMAIL_DOMAIN):
            raise ValueError(f"Email must end with {IFSP_STUDENT_EMAIL_DOMAIN}")
        return email

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, min_length=1)

    @field_validator("email")
    @classmethod
    def validate_student_email(cls, email: Optional[EmailStr]) -> Optional[EmailStr]:
        if email is not None and not str(email).lower().endswith(IFSP_STUDENT_EMAIL_DOMAIN):
            raise ValueError(f"Email must end with {IFSP_STUDENT_EMAIL_DOMAIN}")
        return email

class PasswordUpdate(BaseModel):
    current_password: str = Field(min_length=1)
    new_password: str = Field(min_length=6)

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
