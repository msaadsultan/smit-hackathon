from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    STUDENT = "student"

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None