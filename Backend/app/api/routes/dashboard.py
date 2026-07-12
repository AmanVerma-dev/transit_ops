"""Dashboard routes — read-only aggregation endpoints for the operations dashboard."""
from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import Any

from app.api.dependencies import get_db
from app.api.dependencies.auth import require_roles
from app.models.user import User
from app.repositories.dashboard import DashboardRepository
from app.services.dashboard import DashboardService
from app.schemas.dashboard import (
    DashboardFilter,
    VehicleOverviewResponse,
    DriverOverviewResponse,
    TripOverviewResponse,
    MaintenanceOverviewResponse,
    FinancialOverviewResponse,
    FleetKPIResponse,
    RecentTripsResponse,
    RecentMaintenanceResponse,
)

router = APIRouter()

DASHBOARD_ROLES = ["Fleet Manager", "Financial Analyst", "Safety Officer"]


def get_dashboard_service(db: Session = Depends(get_db)) -> DashboardService:
    return DashboardService(DashboardRepository(db))


# ═══════════════════════════════════════════════════════════════════════

@router.get(
    "/overview",
    response_model=VehicleOverviewResponse,
    summary="Vehicle Overview",
    description="Dashboard summary of all vehicles grouped by status.",
)
def vehicle_overview(
    filters: DashboardFilter = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
) -> Any:
    """
    **Returns:** Total, Available, On Trip, In Maintenance, Retired vehicle counts.

    **Filters:** region
    """
    return service.get_vehicle_overview(filters)


@router.get(
    "/drivers",
    response_model=DriverOverviewResponse,
    summary="Driver Overview",
    description="Dashboard summary of all drivers grouped by status, including expired license count.",
)
def driver_overview(
    filters: DashboardFilter = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
) -> Any:
    """
    **Returns:** Total, Available, On Trip, Suspended drivers, plus expired license count.
    """
    return service.get_driver_overview(filters)


@router.get(
    "/trips",
    response_model=TripOverviewResponse,
    summary="Trip Overview",
    description="Dashboard summary of all trips grouped by status, including today's trip count.",
)
def trip_overview(
    filters: DashboardFilter = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
) -> Any:
    """
    **Returns:** Draft, Dispatched, Completed, Cancelled trip counts plus today's trips.

    **Filters:** vehicle_id, region, start_date, end_date
    """
    return service.get_trip_overview(filters)


@router.get(
    "/maintenance",
    response_model=MaintenanceOverviewResponse,
    summary="Maintenance Overview",
    description="Dashboard summary of all maintenance records grouped by status.",
)
def maintenance_overview(
    filters: DashboardFilter = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
) -> Any:
    """
    **Returns:** Scheduled, In Progress, Completed, Cancelled maintenance counts.

    **Filters:** vehicle_id, region, start_date, end_date
    """
    return service.get_maintenance_overview(filters)


@router.get(
    "/finance",
    response_model=FinancialOverviewResponse,
    summary="Financial Overview",
    description="Dashboard financial summary: revenue, fuel cost, maintenance cost, and profit.",
)
def financial_overview(
    filters: DashboardFilter = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
) -> Any:
    """
    **Returns:** Total revenue, fuel cost, maintenance cost, and net profit.

    **Filters:** vehicle_id, region, start_date, end_date
    """
    return service.get_financial_overview(filters)


@router.get(
    "/kpis",
    response_model=FleetKPIResponse,
    summary="Fleet KPIs",
    description="Key performance indicators: utilization, fuel efficiency, averages.",
)
def fleet_kpis(
    filters: DashboardFilter = Depends(),
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
) -> Any:
    """
    **Returns:** Fleet utilization %, fuel efficiency km/L, average trip distance,
    average revenue, average fuel consumed, total completed trips.

    **Filters:** vehicle_id, region, start_date, end_date
    """
    return service.get_fleet_kpis(filters)


@router.get(
    "/recent-trips",
    response_model=RecentTripsResponse,
    summary="Recent Trips",
    description="Returns the 10 most recent trips.",
)
def recent_trips(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
) -> Any:
    """**Returns:** Latest 10 trips ordered by creation date."""
    return service.get_recent_trips()


@router.get(
    "/recent-maintenance",
    response_model=RecentMaintenanceResponse,
    summary="Recent Maintenance",
    description="Returns the 10 most recent maintenance records.",
)
def recent_maintenance(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: User = Depends(require_roles(DASHBOARD_ROLES)),
) -> Any:
    """**Returns:** Latest 10 maintenance records ordered by creation date."""
    return service.get_recent_maintenance()
