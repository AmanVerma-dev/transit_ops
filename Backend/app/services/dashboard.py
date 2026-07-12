"""Dashboard service — aggregates repository data into dashboard responses."""
import logging
from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import (
    DashboardFilter,
    VehicleOverviewResponse,
    DriverOverviewResponse,
    TripOverviewResponse,
    MaintenanceOverviewResponse,
    FinancialOverviewResponse,
    FleetKPIResponse,
    RecentTripsResponse,
    RecentTripItem,
    RecentMaintenanceResponse,
    RecentMaintenanceItem,
)

logger = logging.getLogger("transitops.dashboard")

FUEL_PRICE_PER_LITER = 1.50


class DashboardService:
    def __init__(self, repo: DashboardRepository):
        self.repo = repo

    def get_vehicle_overview(self, f: DashboardFilter) -> VehicleOverviewResponse:
        counts = self.repo.count_vehicles_by_status(region=f.region)
        total = sum(counts.values())
        logger.info("Vehicle overview: %d total vehicles", total)
        return VehicleOverviewResponse(
            total_vehicles=total,
            available=counts.get("AVAILABLE", 0),
            on_trip=counts.get("ON_TRIP", 0),
            in_maintenance=counts.get("IN_SHOP", 0),
            retired=counts.get("RETIRED", 0),
        )

    def get_driver_overview(self, f: DashboardFilter) -> DriverOverviewResponse:
        counts = self.repo.count_drivers_by_status()
        total = sum(counts.values())
        expired = self.repo.count_expired_licenses()
        logger.info("Driver overview: %d total, %d expired licenses", total, expired)
        return DriverOverviewResponse(
            total_drivers=total,
            available=counts.get("AVAILABLE", 0),
            on_trip=counts.get("ON_TRIP", 0),
            suspended=counts.get("SUSPENDED", 0),
            expired_licenses=expired,
        )

    def get_trip_overview(self, f: DashboardFilter) -> TripOverviewResponse:
        counts = self.repo.count_trips_by_status(
            vehicle_id=f.vehicle_id, region=f.region,
            start_date=f.start_date, end_date=f.end_date,
        )
        todays = self.repo.count_todays_trips()
        logger.info("Trip overview: %d total trips, %d today", sum(counts.values()), todays)
        return TripOverviewResponse(
            draft=counts.get("DRAFT", 0),
            dispatched=counts.get("DISPATCHED", 0),
            completed=counts.get("COMPLETED", 0),
            cancelled=counts.get("CANCELLED", 0),
            todays_trips=todays,
        )

    def get_maintenance_overview(self, f: DashboardFilter) -> MaintenanceOverviewResponse:
        counts = self.repo.count_maintenance_by_status(
            vehicle_id=f.vehicle_id, region=f.region,
            start_date=f.start_date, end_date=f.end_date,
        )
        logger.info("Maintenance overview: %d total records", sum(counts.values()))
        return MaintenanceOverviewResponse(
            scheduled=counts.get("SCHEDULED", 0),
            in_progress=counts.get("IN_PROGRESS", 0),
            completed=counts.get("COMPLETED", 0),
            cancelled=counts.get("CANCELLED", 0),
        )

    def get_financial_overview(self, f: DashboardFilter) -> FinancialOverviewResponse:
        revenue = self.repo.get_total_revenue(
            vehicle_id=f.vehicle_id, region=f.region,
            start_date=f.start_date, end_date=f.end_date,
        )
        fuel_liters = self.repo.get_total_fuel_liters(
            vehicle_id=f.vehicle_id, region=f.region,
            start_date=f.start_date, end_date=f.end_date,
        )
        maint_cost = self.repo.get_total_maintenance_cost(
            vehicle_id=f.vehicle_id, region=f.region,
            start_date=f.start_date, end_date=f.end_date,
        )
        fuel_cost = round(fuel_liters * FUEL_PRICE_PER_LITER, 2)
        total_cost = round(fuel_cost + maint_cost, 2)
        profit = round(revenue - total_cost, 2)
        logger.info("Financial overview: revenue=$%.2f, cost=$%.2f, profit=$%.2f", revenue, total_cost, profit)
        return FinancialOverviewResponse(
            total_revenue=round(revenue, 2),
            fuel_cost=fuel_cost,
            maintenance_cost=round(maint_cost, 2),
            profit=profit,
        )

    def get_fleet_kpis(self, f: DashboardFilter) -> FleetKPIResponse:
        count, avg_dist, avg_rev, total_dist, total_fuel, avg_fuel = self.repo.get_completed_trip_averages(
            vehicle_id=f.vehicle_id, region=f.region,
            start_date=f.start_date, end_date=f.end_date,
        )
        total_vehicles = self.repo.count_active_vehicles(region=f.region)
        vehicles_with_trips = self.repo.count_vehicles_with_completed_trips(
            region=f.region, start_date=f.start_date, end_date=f.end_date,
        )
        utilization = round((vehicles_with_trips / total_vehicles * 100), 2) if total_vehicles > 0 else 0.0
        efficiency = round(float(total_dist) / float(total_fuel), 2) if float(total_fuel) > 0 else 0.0
        logger.info("Fleet KPIs: utilization=%.1f%%, efficiency=%.2f km/L, %d completed trips", utilization, efficiency, count)
        return FleetKPIResponse(
            fleet_utilization_pct=utilization,
            fuel_efficiency_km_per_l=efficiency,
            average_trip_distance_km=round(float(avg_dist), 2),
            average_revenue=round(float(avg_rev), 2),
            average_fuel_consumed_liters=round(float(avg_fuel), 2),
            total_completed_trips=count,
        )

    def get_recent_trips(self) -> RecentTripsResponse:
        trips = self.repo.get_recent_trips(limit=10)
        items = [
            RecentTripItem(
                id=t.id, source=t.source, destination=t.destination,
                vehicle_id=t.vehicle_id, driver_id=t.driver_id,
                status=t.status.value, planned_distance_km=t.planned_distance_km,
                revenue=t.revenue, created_at=t.created_at,
            )
            for t in trips
        ]
        return RecentTripsResponse(items=items)

    def get_recent_maintenance(self) -> RecentMaintenanceResponse:
        records = self.repo.get_recent_maintenance(limit=10)
        items = [
            RecentMaintenanceItem(
                id=r.id, vehicle_id=r.vehicle_id,
                maintenance_type=r.maintenance_type.value,
                description=r.description, status=r.status.value,
                estimated_cost=r.estimated_cost, actual_cost=r.actual_cost,
                scheduled_date=r.scheduled_date,
            )
            for r in records
        ]
        return RecentMaintenanceResponse(items=items)
