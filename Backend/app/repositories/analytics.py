"""Analytics repository — read-only data access for aggregation queries."""
import logging
from sqlmodel import Session, select, func
from typing import Optional, List, Tuple
from datetime import date, datetime, timezone

from app.models.trip import Trip, TripStatus
from app.models.vehicle import Vehicle
from app.models.driver import Driver
from app.models.fuel_log import FuelLog
from app.models.maintenance import Maintenance, MaintenanceStatus

logger = logging.getLogger("transitops.analytics")


class AnalyticsRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Fleet Utilization ──────────────────────────────────────────────

    def count_active_vehicles(self, region: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(Vehicle).where(Vehicle.is_deleted == False)
        if region:
            stmt = stmt.where(Vehicle.region == region)
        return self.session.exec(stmt).one()

    def count_vehicles_with_completed_trips(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> int:
        stmt = (
            select(func.count(func.distinct(Trip.vehicle_id)))
            .select_from(Trip)
            .join(Vehicle, Trip.vehicle_id == Vehicle.id)
            .where(Trip.status == TripStatus.COMPLETED, Vehicle.is_deleted == False)
        )
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        if region:
            stmt = stmt.where(Vehicle.region == region)
        return self.session.exec(stmt).one()

    def count_completed_trips(
        self,
        vehicle_id: Optional[int] = None,
        driver_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> int:
        stmt = select(func.count()).select_from(Trip).where(Trip.status == TripStatus.COMPLETED)
        if vehicle_id:
            stmt = stmt.where(Trip.vehicle_id == vehicle_id)
        if driver_id:
            stmt = stmt.where(Trip.driver_id == driver_id)
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        if region:
            stmt = stmt.join(Vehicle, Trip.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        return self.session.exec(stmt).one()

    # ── Fuel Efficiency ────────────────────────────────────────────────

    def get_fuel_efficiency_by_vehicle(
        self,
        vehicle_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> List[Tuple]:
        """Returns (vehicle_id, registration_number, total_distance, total_fuel)."""
        stmt = (
            select(
                Vehicle.id,
                Vehicle.registration_number,
                func.coalesce(func.sum(Trip.planned_distance_km), 0),
                func.coalesce(func.sum(Trip.fuel_consumed_liters), 0),
            )
            .select_from(Trip)
            .join(Vehicle, Trip.vehicle_id == Vehicle.id)
            .where(Trip.status == TripStatus.COMPLETED, Vehicle.is_deleted == False)
        )
        if vehicle_id:
            stmt = stmt.where(Vehicle.id == vehicle_id)
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        if region:
            stmt = stmt.where(Vehicle.region == region)
        stmt = stmt.group_by(Vehicle.id, Vehicle.registration_number)
        return self.session.exec(stmt).all()

    # ── Operational Cost ───────────────────────────────────────────────

    def get_maintenance_cost_by_vehicle(
        self,
        vehicle_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> List[Tuple]:
        """Returns (vehicle_id, registration_number, total_maintenance_cost)."""
        stmt = (
            select(
                Vehicle.id,
                Vehicle.registration_number,
                func.coalesce(func.sum(Maintenance.actual_cost), 0),
            )
            .select_from(Maintenance)
            .join(Vehicle, Maintenance.vehicle_id == Vehicle.id)
            .where(Maintenance.status == MaintenanceStatus.COMPLETED, Vehicle.is_deleted == False)
        )
        if vehicle_id:
            stmt = stmt.where(Vehicle.id == vehicle_id)
        if start_date:
            stmt = stmt.where(Maintenance.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Maintenance.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        if region:
            stmt = stmt.where(Vehicle.region == region)
        stmt = stmt.group_by(Vehicle.id, Vehicle.registration_number)
        return self.session.exec(stmt).all()

    def get_fuel_liters_by_vehicle(
        self,
        vehicle_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> List[Tuple]:
        """Returns (vehicle_id, registration_number, total_liters)."""
        stmt = (
            select(
                Vehicle.id,
                Vehicle.registration_number,
                func.coalesce(func.sum(FuelLog.liters), 0),
            )
            .select_from(FuelLog)
            .join(Vehicle, FuelLog.vehicle_id == Vehicle.id)
            .where(Vehicle.is_deleted == False)
        )
        if vehicle_id:
            stmt = stmt.where(Vehicle.id == vehicle_id)
        if start_date:
            stmt = stmt.where(FuelLog.recorded_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(FuelLog.recorded_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        if region:
            stmt = stmt.where(Vehicle.region == region)
        stmt = stmt.group_by(Vehicle.id, Vehicle.registration_number)
        return self.session.exec(stmt).all()

    # ── Vehicle ROI ────────────────────────────────────────────────────

    def get_revenue_by_vehicle(
        self,
        vehicle_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> List[Tuple]:
        """Returns (vehicle_id, registration_number, acquisition_cost, total_revenue)."""
        stmt = (
            select(
                Vehicle.id,
                Vehicle.registration_number,
                Vehicle.acquisition_cost,
                func.coalesce(func.sum(Trip.revenue), 0),
            )
            .select_from(Trip)
            .join(Vehicle, Trip.vehicle_id == Vehicle.id)
            .where(Trip.status == TripStatus.COMPLETED, Vehicle.is_deleted == False)
        )
        if vehicle_id:
            stmt = stmt.where(Vehicle.id == vehicle_id)
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        if region:
            stmt = stmt.where(Vehicle.region == region)
        stmt = stmt.group_by(Vehicle.id, Vehicle.registration_number, Vehicle.acquisition_cost)
        return self.session.exec(stmt).all()

    # ── Trip Summary ───────────────────────────────────────────────────

    def get_trip_counts_by_status(
        self,
        vehicle_id: Optional[int] = None,
        driver_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> dict:
        """Returns {status: count}."""
        stmt = select(Trip.status, func.count()).select_from(Trip)
        if vehicle_id:
            stmt = stmt.where(Trip.vehicle_id == vehicle_id)
        if driver_id:
            stmt = stmt.where(Trip.driver_id == driver_id)
        if start_date:
            stmt = stmt.where(Trip.created_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.created_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        if region:
            stmt = stmt.join(Vehicle, Trip.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        stmt = stmt.group_by(Trip.status)
        results = self.session.exec(stmt).all()
        return {s: c for s, c in results}

    def get_trip_averages(
        self,
        vehicle_id: Optional[int] = None,
        driver_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        region: Optional[str] = None,
    ) -> Tuple:
        """Returns (avg_distance, avg_revenue, total_revenue, total_distance) for completed trips."""
        stmt = (
            select(
                func.coalesce(func.avg(Trip.planned_distance_km), 0),
                func.coalesce(func.avg(Trip.revenue), 0),
                func.coalesce(func.sum(Trip.revenue), 0),
                func.coalesce(func.sum(Trip.planned_distance_km), 0),
            )
            .select_from(Trip)
            .where(Trip.status == TripStatus.COMPLETED)
        )
        if vehicle_id:
            stmt = stmt.where(Trip.vehicle_id == vehicle_id)
        if driver_id:
            stmt = stmt.where(Trip.driver_id == driver_id)
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        if region:
            stmt = stmt.join(Vehicle, Trip.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        return self.session.exec(stmt).one()

    # ── CSV Export helpers ─────────────────────────────────────────────

    def get_all_completed_trips(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Trip]:
        stmt = select(Trip).where(Trip.status == TripStatus.COMPLETED)
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        stmt = stmt.order_by(Trip.completed_at.desc())
        return self.session.exec(stmt).all()

    def get_all_fuel_logs(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[FuelLog]:
        stmt = select(FuelLog)
        if start_date:
            stmt = stmt.where(FuelLog.recorded_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(FuelLog.recorded_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        stmt = stmt.order_by(FuelLog.recorded_at.desc())
        return self.session.exec(stmt).all()

    def get_all_maintenance_records(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[Maintenance]:
        stmt = select(Maintenance)
        if start_date:
            stmt = stmt.where(Maintenance.scheduled_date >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Maintenance.scheduled_date <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        stmt = stmt.order_by(Maintenance.scheduled_date.desc())
        return self.session.exec(stmt).all()
