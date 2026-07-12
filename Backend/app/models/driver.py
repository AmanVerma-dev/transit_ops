from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, date, timezone
from enum import Enum

class DriverStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    ON_TRIP = "ON_TRIP"
    OFF_DUTY = "OFF_DUTY"
    SUSPENDED = "SUSPENDED"

class Driver(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    license_number: str = Field(unique=True, index=True, max_length=100)
    license_category: str
    license_expiry_date: date
    contact_number: Optional[str] = None
    safety_score: float = Field(default=100.0, ge=0, le=100)
    status: DriverStatus = Field(default=DriverStatus.AVAILABLE)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_deleted: bool = Field(default=False)
