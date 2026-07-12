from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from app.models.trip import Trip
from app.models.vehicle import Vehicle

class FuelLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    trip_id: int = Field(foreign_key="trip.id")
    vehicle_id: int = Field(foreign_key="vehicle.id")
    liters: float = Field(gt=0)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    trip: Optional[Trip] = Relationship()
    vehicle: Optional[Vehicle] = Relationship()
