"""
Pydantic schemas for authentication.
"""
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from typing import Optional
from models.user import UserRole


class LoginRequest(BaseModel):
    """Schema for login request."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    full_name: str
    role: UserRole


class RegisterRequest(BaseModel):
    """Schema for registering a new user (admin/owner only)."""
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: UserRole


class UserResponse(BaseModel):
    """Schema for user data response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordChange(BaseModel):
    """Schema for changing password."""
    old_password: str
    new_password: str
