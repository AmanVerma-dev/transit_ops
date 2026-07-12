from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.driver import DriverStatus

class DriverBase(BaseModel):
    name: str = Field(..., min_length=2)
    license_number: str = Field(..., min_length=2, max_length=100)
    license_category: str = Field(..., min_length=1)
    license_expiry_date: date
    contact_number: Optional[str] = None
    safety_score: float = Field(default=100.0, ge=0, le=100)
    status: DriverStatus = Field(default=DriverStatus.AVAILABLE)
    user_id: Optional[int] = None

class DriverCreate(DriverBase):
    pass

class DriverUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2)
    license_category: Optional[str] = Field(None, min_length=1)
    license_expiry_date: Optional[date] = None
    contact_number: Optional[str] = None
    safety_score: Optional[float] = Field(None, ge=0, le=100)
    status: Optional[DriverStatus] = None
    user_id: Optional[int] = None

class DriverResponse(DriverBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class DriverListResponse(BaseModel):
    total: int
    items: List[DriverResponse]

class DriverFilter(BaseModel):
    status: Optional[DriverStatus] = None
    license_category: Optional[str] = None
    expired_license: Optional[bool] = None
    search_name: Optional[str] = None
    search_license: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=100)
