from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.vehicle import VehicleStatus

class VehicleBase(BaseModel):
    registration_number: str = Field(..., min_length=2, max_length=50)
    name_model: str = Field(..., min_length=1)
    type: str = Field(..., min_length=1)
    max_load_capacity_kg: float = Field(..., gt=0)
    odometer_km: float = Field(default=0.0, ge=0)
    acquisition_cost: float = Field(..., ge=0)
    status: VehicleStatus = Field(default=VehicleStatus.AVAILABLE)
    region: Optional[str] = None

class VehicleCreate(VehicleBase):
    pass

class VehicleUpdate(BaseModel):
    name_model: Optional[str] = Field(None, min_length=1)
    type: Optional[str] = Field(None, min_length=1)
    max_load_capacity_kg: Optional[float] = Field(None, gt=0)
    odometer_km: Optional[float] = Field(None, ge=0)
    status: Optional[VehicleStatus] = None
    region: Optional[str] = None

class VehicleResponse(VehicleBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class VehicleListResponse(BaseModel):
    total: int
    items: List[VehicleResponse]

class VehicleFilter(BaseModel):
    status: Optional[VehicleStatus] = None
    type: Optional[str] = None
    region: Optional[str] = None
    registration_search: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=100)
