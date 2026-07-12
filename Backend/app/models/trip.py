from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from enum import Enum
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.user import User

class TripStatus(str, Enum):
    DRAFT = "DRAFT"
    DISPATCHED = "DISPATCHED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class Trip(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    source: str
    destination: str
    vehicle_id: int = Field(foreign_key="vehicle.id")
    driver_id: int = Field(foreign_key="driver.id")
    cargo_weight_kg: float = Field(gt=0)
    planned_distance_km: float = Field(gt=0)
    status: TripStatus = Field(default=TripStatus.DRAFT)
    
    # Lifecycle tracking fields
    dispatched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    # Completion metrics
    final_odometer: Optional[float] = None
    fuel_consumed_liters: Optional[float] = None
    revenue: Optional[float] = None
    
    created_by: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    vehicle: Optional[Vehicle] = Relationship()
    driver: Optional[Driver] = Relationship()
    creator: Optional[User] = Relationship()
