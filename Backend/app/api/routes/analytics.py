"""Analytics & Reports routes — read-only endpoints for aggregated operational data."""
import csv
import io
from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import Any, Optional
from datetime import date

from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_active_user, require_roles
from app.models.user import User
from app.repositories.analytics import AnalyticsRepository
from app.services.analytics import AnalyticsService
from app.schemas.analytics import (
    AnalyticsFilter,
    FleetUtilizationResponse,
    FuelEfficiencyResponse,
    OperationalCostResponse,
    VehicleROIResponse,
    TripSummaryResponse,
)

analytics_router = APIRouter()
reports_router = APIRouter()


def get_analytics_service(db: Session = Depends(get_db)) -> AnalyticsService:
    return AnalyticsService(AnalyticsRepository(db))


def get_analytics_repo(db: Session = Depends(get_db)) -> AnalyticsRepository:
    return AnalyticsRepository(db)


# ═══════════════════════════════════════════════════════════════════════
# ANALYTICS ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@analytics_router.get(
    "/fleet-utilization",
    response_model=FleetUtilizationResponse,
    summary="Fleet Utilization",
    description="Calculate fleet utilization percentage based on vehicles with completed trips vs total vehicles.",
)
def fleet_utilization(
    filters: AnalyticsFilter = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Financial Analyst", "Safety Officer"])),
) -> Any:
    """
    **Formula:** (Vehicles with completed trips / Total vehicles) × 100

    **Filters:** vehicle_id, driver_id, start_date, end_date, region
    """
    return service.get_fleet_utilization(filters)


@analytics_router.get(
    "/fuel-efficiency",
    response_model=FuelEfficiencyResponse,
    summary="Fuel Efficiency",
    description="Calculate fuel efficiency (km/L) per vehicle and fleet average.",
)
def fuel_efficiency(
    filters: AnalyticsFilter = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Financial Analyst", "Safety Officer"])),
) -> Any:
    """
    **Formula:** Distance Travelled / Fuel Consumed (km/L)

    **Filters:** vehicle_id, start_date, end_date, region
    """
    return service.get_fuel_efficiency(filters)


@analytics_router.get(
    "/operational-cost",
    response_model=OperationalCostResponse,
    summary="Operational Cost",
    description="Calculate total operational costs broken down by fuel and maintenance per vehicle.",
)
def operational_cost(
    filters: AnalyticsFilter = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Financial Analyst", "Safety Officer"])),
) -> Any:
    """
    **Formula:** Fuel Cost + Maintenance Cost

    **Filters:** vehicle_id, start_date, end_date, region
    """
    return service.get_operational_cost(filters)


@analytics_router.get(
    "/vehicle-roi",
    response_model=VehicleROIResponse,
    summary="Vehicle ROI",
    description="Calculate return on investment per vehicle: Revenue minus Operating Cost.",
)
def vehicle_roi(
    filters: AnalyticsFilter = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Financial Analyst", "Safety Officer"])),
) -> Any:
    """
    **Formula:** Revenue - Operating Cost

    **Filters:** vehicle_id, start_date, end_date, region
    """
    return service.get_vehicle_roi(filters)


@analytics_router.get(
    "/trip-summary",
    response_model=TripSummaryResponse,
    summary="Trip Summary",
    description="Aggregate trip statistics: counts by status, average distance, average revenue.",
)
def trip_summary(
    filters: AnalyticsFilter = Depends(),
    service: AnalyticsService = Depends(get_analytics_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Financial Analyst", "Safety Officer"])),
) -> Any:
    """
    **Returns:** Completed, cancelled, active, and draft trip counts plus averages.

    **Filters:** vehicle_id, driver_id, start_date, end_date, region
    """
    return service.get_trip_summary(filters)


# ═══════════════════════════════════════════════════════════════════════
# CSV EXPORT ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════

@reports_router.get(
    "/export/trips",
    summary="Export Trips CSV",
    description="Export completed trips data as a CSV file.",
)
def export_trips_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    repo: AnalyticsRepository = Depends(get_analytics_repo),
    current_user: User = Depends(require_roles(["Fleet Manager", "Financial Analyst"])),
) -> StreamingResponse:
    trips = repo.get_all_completed_trips(start_date=start_date, end_date=end_date)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "source", "destination", "vehicle_id", "driver_id",
                      "cargo_weight_kg", "planned_distance_km", "status",
                      "revenue", "fuel_consumed_liters", "final_odometer",
                      "dispatched_at", "completed_at"])
    for t in trips:
        writer.writerow([
            t.id, t.source, t.destination, t.vehicle_id, t.driver_id,
            t.cargo_weight_kg, t.planned_distance_km, t.status.value,
            t.revenue, t.fuel_consumed_liters, t.final_odometer,
            t.dispatched_at, t.completed_at,
        ])
    output.seek(0)
    return StreamingResponse(
        output, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=trips_export.csv"},
    )


@reports_router.get(
    "/export/fuel",
    summary="Export Fuel Logs CSV",
    description="Export fuel log data as a CSV file.",
)
def export_fuel_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    repo: AnalyticsRepository = Depends(get_analytics_repo),
    current_user: User = Depends(require_roles(["Fleet Manager", "Financial Analyst"])),
) -> StreamingResponse:
    logs = repo.get_all_fuel_logs(start_date=start_date, end_date=end_date)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "trip_id", "vehicle_id", "liters", "recorded_at"])
    for log in logs:
        writer.writerow([log.id, log.trip_id, log.vehicle_id, log.liters, log.recorded_at])
    output.seek(0)
    return StreamingResponse(
        output, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=fuel_export.csv"},
    )


@reports_router.get(
    "/export/maintenance",
    summary="Export Maintenance CSV",
    description="Export maintenance records as a CSV file.",
)
def export_maintenance_csv(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    repo: AnalyticsRepository = Depends(get_analytics_repo),
    current_user: User = Depends(require_roles(["Fleet Manager", "Financial Analyst"])),
) -> StreamingResponse:
    records = repo.get_all_maintenance_records(start_date=start_date, end_date=end_date)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "vehicle_id", "maintenance_type", "description",
                      "scheduled_date", "started_at", "completed_at",
                      "estimated_cost", "actual_cost", "status", "technician_notes"])
    for r in records:
        writer.writerow([
            r.id, r.vehicle_id, r.maintenance_type.value, r.description,
            r.scheduled_date, r.started_at, r.completed_at,
            r.estimated_cost, r.actual_cost, r.status.value, r.technician_notes,
        ])
    output.seek(0)
    return StreamingResponse(
        output, media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=maintenance_export.csv"},
    )
