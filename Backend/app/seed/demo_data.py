"""Seed demo operational data for hackathon demonstration."""
import logging
from datetime import datetime, timedelta, timezone, date
from sqlmodel import Session

from app.models.vehicle import Vehicle, VehicleStatus
from app.models.driver import Driver, DriverStatus
from app.models.trip import Trip, TripStatus
from app.models.maintenance import Maintenance, MaintenanceStatus, MaintenanceType
from app.models.fuel_log import FuelLog
from app.repositories.vehicle import VehicleRepository
from app.repositories.driver import DriverRepository

logger = logging.getLogger("transitops.seed")

DEMO_VEHICLES = [
    {"registration_number": "TRK-1001", "name_model": "Volvo FH16", "type": "Truck", "max_load_capacity_kg": 25000, "acquisition_cost": 185000, "region": "North"},
    {"registration_number": "TRK-1002", "name_model": "Scania R500", "type": "Truck", "max_load_capacity_kg": 22000, "acquisition_cost": 165000, "region": "North"},
    {"registration_number": "BUS-2001", "name_model": "Mercedes Citaro", "type": "Bus", "max_load_capacity_kg": 8000, "acquisition_cost": 320000, "region": "South"},
    {"registration_number": "VAN-3001", "name_model": "Ford Transit", "type": "Van", "max_load_capacity_kg": 1500, "acquisition_cost": 45000, "region": "East"},
    {"registration_number": "TRK-1003", "name_model": "MAN TGX", "type": "Truck", "max_load_capacity_kg": 20000, "acquisition_cost": 155000, "region": "West"},
]

DEMO_DRIVERS = [
    {"name": "Rajesh Kumar", "license_number": "DL-2024-001", "license_category": "HMV", "license_expiry_date": "2028-06-15", "contact_number": "+91-98765-43210", "safety_score": 95.0},
    {"name": "Priya Sharma", "license_number": "DL-2024-002", "license_category": "HMV", "license_expiry_date": "2029-03-20", "contact_number": "+91-98765-43211", "safety_score": 98.0},
    {"name": "Amit Patel", "license_number": "DL-2024-003", "license_category": "LMV", "license_expiry_date": "2027-11-01", "contact_number": "+91-98765-43212", "safety_score": 88.0},
    {"name": "Sunita Verma", "license_number": "DL-2024-004", "license_category": "HMV", "license_expiry_date": "2025-01-10", "contact_number": "+91-98765-43213", "safety_score": 92.0},
]


def seed_demo_data(session: Session) -> None:
    """Seed sample vehicles, drivers, trips, maintenance, and fuel logs for demo."""
    vehicle_repo = VehicleRepository(session)
    driver_repo = DriverRepository(session)

    # ── Vehicles ───────────────────────────────────────────────────
    existing = vehicle_repo.get_by_registration(DEMO_VEHICLES[0]["registration_number"])
    if existing:
        logger.info("Demo data already seeded. Skipping.")
        return

    vehicles = []
    for v_data in DEMO_VEHICLES:
        v = Vehicle(**v_data)
        session.add(v)
        session.flush()
        vehicles.append(v)
        logger.info("Demo vehicle '%s' created.", v.registration_number)

    # ── Drivers ────────────────────────────────────────────────────
    drivers = []
    for d_data in DEMO_DRIVERS:
        d_data_copy = d_data.copy()
        d_data_copy["license_expiry_date"] = date.fromisoformat(d_data_copy["license_expiry_date"])
        d = Driver(**d_data_copy)
        session.add(d)
        session.flush()
        drivers.append(d)
        logger.info("Demo driver '%s' created.", d.name)

    # ── Completed Trips ────────────────────────────────────────────
    now = datetime.now(timezone.utc)
    trip_configs = [
        {"source": "Mumbai", "destination": "Pune", "vehicle": vehicles[0], "driver": drivers[0], "cargo": 15000, "dist": 150, "revenue": 25000, "fuel": 45, "days_ago": 7},
        {"source": "Delhi", "destination": "Jaipur", "vehicle": vehicles[1], "driver": drivers[1], "cargo": 18000, "dist": 280, "revenue": 42000, "fuel": 85, "days_ago": 5},
        {"source": "Bangalore", "destination": "Chennai", "vehicle": vehicles[2], "driver": drivers[2], "cargo": 5000, "dist": 350, "revenue": 18000, "fuel": 65, "days_ago": 3},
        {"source": "Mumbai", "destination": "Ahmedabad", "vehicle": vehicles[0], "driver": drivers[0], "cargo": 20000, "dist": 530, "revenue": 55000, "fuel": 160, "days_ago": 2},
        {"source": "Kolkata", "destination": "Patna", "vehicle": vehicles[3], "driver": drivers[3], "cargo": 1200, "dist": 600, "revenue": 12000, "fuel": 50, "days_ago": 1},
    ]

    odo_tracker = {v.id: 0.0 for v in vehicles}

    # Get the first user (Fleet Manager) for created_by
    from app.repositories.user import UserRepository
    user_repo = UserRepository(session)
    manager = user_repo.get_by_email("manager@transitops.com")
    creator_id = manager.id if manager else 1

    for tc in trip_configs:
        v = tc["vehicle"]
        d = tc["driver"]
        completed_at = now - timedelta(days=tc["days_ago"])
        odo_tracker[v.id] += tc["dist"]
        trip = Trip(
            source=tc["source"], destination=tc["destination"],
            vehicle_id=v.id, driver_id=d.id,
            cargo_weight_kg=tc["cargo"], planned_distance_km=tc["dist"],
            status=TripStatus.COMPLETED, created_by=creator_id,
            dispatched_at=completed_at - timedelta(hours=tc["dist"] / 60),
            completed_at=completed_at,
            final_odometer=odo_tracker[v.id],
            fuel_consumed_liters=tc["fuel"], revenue=tc["revenue"],
        )
        session.add(trip)
        session.flush()

        fuel_log = FuelLog(trip_id=trip.id, vehicle_id=v.id, liters=tc["fuel"], recorded_at=completed_at)
        session.add(fuel_log)
        logger.info("Demo trip '%s → %s' created.", tc["source"], tc["destination"])

    # Update vehicle odometers
    for v in vehicles:
        v.odometer_km = odo_tracker[v.id]
        session.add(v)

    # ── A dispatched trip (active) ──────────────────────────────────
    active_trip = Trip(
        source="Hyderabad", destination="Vizag",
        vehicle_id=vehicles[4].id, driver_id=drivers[3].id,
        cargo_weight_kg=12000, planned_distance_km=620,
        status=TripStatus.DISPATCHED, created_by=creator_id,
        dispatched_at=now - timedelta(hours=3),
    )
    vehicles[4].status = VehicleStatus.ON_TRIP
    drivers[3].status = DriverStatus.ON_TRIP
    session.add(active_trip)
    session.add(vehicles[4])
    session.add(drivers[3])

    # ── A cancelled trip ────────────────────────────────────────────
    cancelled_trip = Trip(
        source="Goa", destination="Mumbai",
        vehicle_id=vehicles[0].id, driver_id=drivers[0].id,
        cargo_weight_kg=8000, planned_distance_km=590,
        status=TripStatus.CANCELLED, created_by=creator_id,
        cancelled_at=now - timedelta(days=4),
    )
    session.add(cancelled_trip)

    # ── A draft trip ────────────────────────────────────────────────
    draft_trip = Trip(
        source="Lucknow", destination="Varanasi",
        vehicle_id=vehicles[0].id, driver_id=drivers[0].id,
        cargo_weight_kg=10000, planned_distance_km=320,
        status=TripStatus.DRAFT, created_by=creator_id,
    )
    session.add(draft_trip)

    # ── Maintenance Records ─────────────────────────────────────────
    maint_configs = [
        {"vehicle": vehicles[0], "type": MaintenanceType.PREVENTIVE, "desc": "Quarterly oil change and filter replacement", "est": 8500, "act": 7800, "status": MaintenanceStatus.COMPLETED, "days_ago": 10},
        {"vehicle": vehicles[1], "type": MaintenanceType.CORRECTIVE, "desc": "Brake pad replacement - front axle", "est": 15000, "act": 14200, "status": MaintenanceStatus.COMPLETED, "days_ago": 6},
        {"vehicle": vehicles[2], "type": MaintenanceType.INSPECTION, "desc": "Annual fitness certificate inspection", "est": 3000, "act": None, "status": MaintenanceStatus.SCHEDULED, "days_ago": -5},
        {"vehicle": vehicles[0], "type": MaintenanceType.EMERGENCY, "desc": "Coolant leak repair", "est": 12000, "act": None, "status": MaintenanceStatus.IN_PROGRESS, "days_ago": 0},
    ]

    for mc in maint_configs:
        sched_date = now + timedelta(days=-mc["days_ago"]) if mc["days_ago"] >= 0 else now + timedelta(days=abs(mc["days_ago"]))
        m = Maintenance(
            vehicle_id=mc["vehicle"].id, maintenance_type=mc["type"],
            description=mc["desc"], scheduled_date=sched_date,
            estimated_cost=mc["est"], actual_cost=mc["act"],
            status=mc["status"], created_by=creator_id,
        )
        if mc["status"] in [MaintenanceStatus.IN_PROGRESS, MaintenanceStatus.COMPLETED]:
            m.started_at = sched_date
        if mc["status"] == MaintenanceStatus.COMPLETED:
            m.completed_at = sched_date + timedelta(hours=4)
        session.add(m)
        logger.info("Demo maintenance '%s' created for %s.", mc["desc"][:40], mc["vehicle"].registration_number)

    session.commit()
    logger.info("Demo operational data seeded successfully.")
