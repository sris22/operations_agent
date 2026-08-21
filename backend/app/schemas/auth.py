from enum import Enum

from pydantic import BaseModel


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    OPERATOR = "OPERATOR"


class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole | None = UserRole.OPERATOR


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
