from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List
from datetime import datetime
from app.schemas.enums import UserRole

class LoginRequest(BaseModel):
    mobile: str
    password: str

    @validator('mobile')
    def validate_mobile(cls, v):
        v = v.strip()
        if not 10 <= len(v) <= 15:
            raise ValueError('Mobile number must be between 10 and 15 characters')
        return v

class RegisterRequest(BaseModel):
    mobile: str
    password: str
    first_name: str
    last_name: str
    address: str
    city: str
    state: str
    zip_code: str
    email: Optional[EmailStr] = None

    @validator('mobile')
    def validate_mobile(cls, v):
        v = v.strip()
        if not 10 <= len(v) <= 15:
            raise ValueError('Mobile number must be between 10 and 15 characters')
        return v

class UserProfile(BaseModel):
    id: str
    mobile: str
    email: Optional[EmailStr] = None
    first_name: str = None
    last_name: str = None
    address: str = None
    city: str = None
    state: str = None
    zip_code: str = None
    role: UserRole
    shop_ids: List[int] = []
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_user_and_customer(cls, user, customer):
        return cls(
            id=user.id,
            mobile=user.mobile,
            email=user.email,
            first_name=customer.first_name if customer else None,
            last_name=customer.last_name if customer else None,
            address=customer.address if customer else None,
            city=customer.city if customer else None,
            state=customer.state if customer else None,
            zip_code=customer.zip_code if customer else None,
            role=user.role,
            shop_ids=[shop.id for shop in user.shops],
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None

class UserCreateAdmin(BaseModel):
    mobile: str
    password: str
    first_name: str
    last_name: str
    role: UserRole
    shop_ids: List[int] = []

class AuthResponse(BaseModel):
    token: str
    user: UserProfile