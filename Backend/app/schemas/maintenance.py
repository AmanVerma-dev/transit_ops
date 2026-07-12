from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.models.maintenance import MaintenanceStatus, MaintenanceType

class MaintenanceBase(BaseModel):
    vehicle_id: int = Field(..., gt=0)
    maintenance_type: MaintenanceType
    description: str = Field(..., min_length=1)
    scheduled_date: datetime
    estimated_cost: float = Field(..., ge=0)
    technician_notes: Optional[str] = None

class MaintenanceCreate(MaintenanceBase):
    pass

class MaintenanceUpdate(BaseModel):
    maintenance_type: Optional[MaintenanceType] = None
    description: Optional[str] = Field(None, min_length=1)
    scheduled_date: Optional[datetime] = None
    estimated_cost: Optional[float] = Field(None, ge=0)
    actual_cost: Optional[float] = Field(None, ge=0)
    technician_notes: Optional[str] = None

class MaintenanceResponse(MaintenanceBase):
    id: int
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    actual_cost: Optional[float] = None
    status: MaintenanceStatus
    created_by: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MaintenanceListResponse(BaseModel):
    total: int
    items: List[MaintenanceResponse]

class MaintenanceFilter(BaseModel):
    vehicle_id: Optional[int] = Field(None, gt=0)
    status: Optional[MaintenanceStatus] = None
    maintenance_type: Optional[MaintenanceType] = None
    scheduled_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=100)
