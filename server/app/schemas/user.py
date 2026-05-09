from pydantic import BaseModel, EmailStr, ConfigDict, field_validator
from app.models.models import RoleType

IFSP_STUDENT_EMAIL_DOMAIN = "@aluno.ifsp.edu.br"

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: str
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

class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
