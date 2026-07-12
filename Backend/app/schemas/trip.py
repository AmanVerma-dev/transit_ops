from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from app.models.trip import TripStatus

class TripBase(BaseModel):
    source: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    vehicle_id: int
    driver_id: int
    cargo_weight_kg: float = Field(..., gt=0)
    planned_distance_km: float = Field(..., gt=0)

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    source: Optional[str] = Field(None, min_length=1)
    destination: Optional[str] = Field(None, min_length=1)
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    cargo_weight_kg: Optional[float] = Field(None, gt=0)
    planned_distance_km: Optional[float] = Field(None, gt=0)

class TripComplete(BaseModel):
    final_odometer: float = Field(..., ge=0)
    fuel_consumed_liters: float = Field(..., ge=0)
    revenue: float = Field(..., ge=0)

class TripResponse(TripBase):
    id: int
    status: TripStatus
    dispatched_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    final_odometer: Optional[float] = None
    fuel_consumed_liters: Optional[float] = None
    revenue: Optional[float] = None
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TripListResponse(BaseModel):
    total: int
    items: List[TripResponse]

class TripFilter(BaseModel):
    status: Optional[TripStatus] = None
    vehicle_id: Optional[int] = None
    driver_id: Optional[int] = None
    created_by: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=100)
