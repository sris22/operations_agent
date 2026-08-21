from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


class UserCreate(BaseModel):
    email: str
    password: str
    role: Optional[UserRole] = UserRole.OPERATOR


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    role: str
    email: str


class UserResponse(BaseModel):
    id: int
    email: str
    role: str
