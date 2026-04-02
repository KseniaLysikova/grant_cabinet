from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models import UserRole
from app.schemas.common import ORMBase


class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)
    role: UserRole = UserRole.applicant

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 128:
            raise ValueError("Пароль слишком длинный")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)

    @field_validator("password")
    @classmethod
    def validate_password_length(cls, value: str) -> str:
        if len(value.encode("utf-8")) > 128:
            raise ValueError("Пароль слишком длинный")
        return value


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(ORMBase):
    id: int
    full_name: str
    email: EmailStr
    role: UserRole
    is_active: bool
    created_at: datetime