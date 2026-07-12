"""Dashboard repository — read-only count and aggregate queries."""
import logging
from sqlmodel import Session, select, func
from typing import Optional, List
from datetime import date, datetime, timezone

from app.models.vehicle import Vehicle, VehicleStatus
from app.models.driver import Driver, DriverStatus
from app.models.trip import Trip, TripStatus
from app.models.maintenance import Maintenance, MaintenanceStatus
from app.models.fuel_log import FuelLog

logger = logging.getLogger("transitops.dashboard")


class DashboardRepository:
    def __init__(self, session: Session):
        self.session = session

    # ── Vehicle counts ─────────────────────────────────────────────────

    def count_vehicles_by_status(self, region: Optional[str] = None) -> dict:
        stmt = (
            select(Vehicle.status, func.count())
            .where(Vehicle.is_deleted == False)
        )
        if region:
            stmt = stmt.where(Vehicle.region == region)
        stmt = stmt.group_by(Vehicle.status)
        results = self.session.exec(stmt).all()
        return {s.value: c for s, c in results}

    # ── Driver counts ──────────────────────────────────────────────────

    def count_drivers_by_status(self) -> dict:
        stmt = (
            select(Driver.status, func.count())
            .where(Driver.is_deleted == False)
            .group_by(Driver.status)
        )
        results = self.session.exec(stmt).all()
        return {s.value: c for s, c in results}

    def count_expired_licenses(self) -> int:
        today = date.today()
        stmt = (
            select(func.count())
            .select_from(Driver)
            .where(Driver.is_deleted == False, Driver.license_expiry_date < today)
        )
        return self.session.exec(stmt).one()

    # ── Trip counts ────────────────────────────────────────────────────

    def count_trips_by_status(
        self,
        vehicle_id: Optional[int] = None,
        region: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:
        stmt = select(Trip.status, func.count()).select_from(Trip)
        if vehicle_id:
            stmt = stmt.where(Trip.vehicle_id == vehicle_id)
        if region:
            stmt = stmt.join(Vehicle, Trip.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        if start_date:
            stmt = stmt.where(Trip.created_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.created_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        stmt = stmt.group_by(Trip.status)
        results = self.session.exec(stmt).all()
        return {s.value: c for s, c in results}

    def count_todays_trips(self) -> int:
        today = date.today()
        start = datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc)
        end = datetime.combine(today, datetime.max.time(), tzinfo=timezone.utc)
        stmt = select(func.count()).select_from(Trip).where(Trip.created_at >= start, Trip.created_at <= end)
        return self.session.exec(stmt).one()

    # ── Maintenance counts ─────────────────────────────────────────────

    def count_maintenance_by_status(
        self,
        vehicle_id: Optional[int] = None,
        region: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> dict:
        stmt = select(Maintenance.status, func.count()).select_from(Maintenance)
        if vehicle_id:
            stmt = stmt.where(Maintenance.vehicle_id == vehicle_id)
        if region:
            stmt = stmt.join(Vehicle, Maintenance.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        if start_date:
            stmt = stmt.where(Maintenance.scheduled_date >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Maintenance.scheduled_date <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        stmt = stmt.group_by(Maintenance.status)
        results = self.session.exec(stmt).all()
        return {s.value: c for s, c in results}

    # ── Financial aggregates ───────────────────────────────────────────

    def get_total_revenue(
        self,
        vehicle_id: Optional[int] = None,
        region: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> float:
        stmt = select(func.coalesce(func.sum(Trip.revenue), 0)).where(Trip.status == TripStatus.COMPLETED)
        if vehicle_id:
            stmt = stmt.where(Trip.vehicle_id == vehicle_id)
        if region:
            stmt = stmt.join(Vehicle, Trip.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        return float(self.session.exec(stmt).one())

    def get_total_fuel_liters(
        self,
        vehicle_id: Optional[int] = None,
        region: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> float:
        stmt = select(func.coalesce(func.sum(FuelLog.liters), 0)).select_from(FuelLog)
        if vehicle_id:
            stmt = stmt.where(FuelLog.vehicle_id == vehicle_id)
        if region:
            stmt = stmt.join(Vehicle, FuelLog.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        if start_date:
            stmt = stmt.where(FuelLog.recorded_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(FuelLog.recorded_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        return float(self.session.exec(stmt).one())

    def get_total_maintenance_cost(
        self,
        vehicle_id: Optional[int] = None,
        region: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> float:
        stmt = (
            select(func.coalesce(func.sum(Maintenance.actual_cost), 0))
            .where(Maintenance.status == MaintenanceStatus.COMPLETED)
        )
        if vehicle_id:
            stmt = stmt.where(Maintenance.vehicle_id == vehicle_id)
        if region:
            stmt = stmt.join(Vehicle, Maintenance.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        if start_date:
            stmt = stmt.where(Maintenance.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Maintenance.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        return float(self.session.exec(stmt).one())

    # ── KPI aggregates ─────────────────────────────────────────────────

    def get_completed_trip_averages(
        self,
        vehicle_id: Optional[int] = None,
        region: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> tuple:
        """Returns (count, avg_distance, avg_revenue, total_distance, total_fuel, avg_fuel)."""
        stmt = (
            select(
                func.count(),
                func.coalesce(func.avg(Trip.planned_distance_km), 0),
                func.coalesce(func.avg(Trip.revenue), 0),
                func.coalesce(func.sum(Trip.planned_distance_km), 0),
                func.coalesce(func.sum(Trip.fuel_consumed_liters), 0),
                func.coalesce(func.avg(Trip.fuel_consumed_liters), 0),
            )
            .where(Trip.status == TripStatus.COMPLETED)
        )
        if vehicle_id:
            stmt = stmt.where(Trip.vehicle_id == vehicle_id)
        if region:
            stmt = stmt.join(Vehicle, Trip.vehicle_id == Vehicle.id).where(Vehicle.region == region)
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        return self.session.exec(stmt).one()

    def count_active_vehicles(self, region: Optional[str] = None) -> int:
        stmt = select(func.count()).select_from(Vehicle).where(Vehicle.is_deleted == False)
        if region:
            stmt = stmt.where(Vehicle.region == region)
        return self.session.exec(stmt).one()

    def count_vehicles_with_completed_trips(
        self,
        region: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        stmt = (
            select(func.count(func.distinct(Trip.vehicle_id)))
            .select_from(Trip)
            .join(Vehicle, Trip.vehicle_id == Vehicle.id)
            .where(Trip.status == TripStatus.COMPLETED, Vehicle.is_deleted == False)
        )
        if region:
            stmt = stmt.where(Vehicle.region == region)
        if start_date:
            stmt = stmt.where(Trip.completed_at >= datetime.combine(start_date, datetime.min.time(), tzinfo=timezone.utc))
        if end_date:
            stmt = stmt.where(Trip.completed_at <= datetime.combine(end_date, datetime.max.time(), tzinfo=timezone.utc))
        return self.session.exec(stmt).one()

    # ── Recent activity ────────────────────────────────────────────────

    def get_recent_trips(self, limit: int = 10) -> List[Trip]:
        stmt = select(Trip).order_by(Trip.created_at.desc()).limit(limit)
        return self.session.exec(stmt).all()

    def get_recent_maintenance(self, limit: int = 10) -> List[Maintenance]:
        stmt = select(Maintenance).order_by(Maintenance.created_at.desc()).limit(limit)
        return self.session.exec(stmt).all()
