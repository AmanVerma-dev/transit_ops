from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(min_length=8)
    role_name: str = "Driver" # Default role if none provided

class UserResponse(UserBase):
    id: int
    role_id: Optional[int]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
