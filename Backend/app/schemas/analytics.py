"""Analytics schemas for response models and filters."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class AnalyticsFilter(BaseModel):
    """Common filter for all analytics endpoints."""
    vehicle_id: Optional[int] = Field(None, gt=0, description="Filter by vehicle ID")
    driver_id: Optional[int] = Field(None, gt=0, description="Filter by driver ID")
    start_date: Optional[date] = Field(None, description="Start of date range")
    end_date: Optional[date] = Field(None, description="End of date range")
    region: Optional[str] = Field(None, description="Filter by vehicle region")


class FleetUtilizationResponse(BaseModel):
    total_vehicles: int
    vehicles_with_completed_trips: int
    utilization_percentage: float
    total_completed_trips: int


class FuelEfficiencyItem(BaseModel):
    vehicle_id: int
    registration_number: str
    total_distance_km: float
    total_fuel_liters: float
    efficiency_km_per_liter: float


class FuelEfficiencyResponse(BaseModel):
    items: List[FuelEfficiencyItem]
    fleet_avg_efficiency: float


class OperationalCostResponse(BaseModel):
    total_fuel_cost_estimate: float
    total_maintenance_cost: float
    total_cost: float
    breakdown_by_vehicle: List[dict]


class VehicleROIItem(BaseModel):
    vehicle_id: int
    registration_number: str
    acquisition_cost: float
    total_revenue: float
    total_operating_cost: float
    net_roi: float


class VehicleROIResponse(BaseModel):
    items: List[VehicleROIItem]
    fleet_total_revenue: float
    fleet_total_cost: float
    fleet_net_roi: float


class TripSummaryResponse(BaseModel):
    total_trips: int
    completed_trips: int
    cancelled_trips: int
    active_trips: int
    draft_trips: int
    average_distance_km: float
    average_revenue: float
    total_revenue: float
    total_distance_km: float
