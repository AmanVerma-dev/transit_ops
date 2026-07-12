"""Dashboard schemas — response models for all dashboard endpoints."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class DashboardFilter(BaseModel):
    """Common filter for dashboard endpoints."""
    vehicle_id: Optional[int] = Field(None, gt=0, description="Filter by vehicle ID")
    region: Optional[str] = Field(None, description="Filter by vehicle region")
    start_date: Optional[date] = Field(None, description="Start of date range")
    end_date: Optional[date] = Field(None, description="End of date range")


# ── Vehicle Overview ───────────────────────────────────────────────────

class VehicleOverviewResponse(BaseModel):
    total_vehicles: int
    available: int
    on_trip: int
    in_maintenance: int
    retired: int


# ── Driver Overview ────────────────────────────────────────────────────

class DriverOverviewResponse(BaseModel):
    total_drivers: int
    available: int
    on_trip: int
    suspended: int
    expired_licenses: int


# ── Trip Overview ──────────────────────────────────────────────────────

class TripOverviewResponse(BaseModel):
    draft: int
    dispatched: int
    completed: int
    cancelled: int
    todays_trips: int


# ── Maintenance Overview ──────────────────────────────────────────────

class MaintenanceOverviewResponse(BaseModel):
    scheduled: int
    in_progress: int
    completed: int
    cancelled: int


# ── Financial Overview ────────────────────────────────────────────────

class FinancialOverviewResponse(BaseModel):
    total_revenue: float
    fuel_cost: float
    maintenance_cost: float
    profit: float


# ── Fleet KPIs ────────────────────────────────────────────────────────

class FleetKPIResponse(BaseModel):
    fleet_utilization_pct: float
    fuel_efficiency_km_per_l: float
    average_trip_distance_km: float
    average_revenue: float
    average_fuel_consumed_liters: float
    total_completed_trips: int


# ── Recent Activity ───────────────────────────────────────────────────

class RecentTripItem(BaseModel):
    id: int
    source: str
    destination: str
    vehicle_id: int
    driver_id: int
    status: str
    planned_distance_km: float
    revenue: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class RecentMaintenanceItem(BaseModel):
    id: int
    vehicle_id: int
    maintenance_type: str
    description: str
    status: str
    estimated_cost: float
    actual_cost: Optional[float] = None
    scheduled_date: datetime

    class Config:
        from_attributes = True


class RecentTripsResponse(BaseModel):
    items: List[RecentTripItem]


class RecentMaintenanceResponse(BaseModel):
    items: List[RecentMaintenanceItem]
