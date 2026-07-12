from fastapi import HTTPException, status
from typing import Tuple, Sequence
from datetime import datetime, timezone, date
from app.models.trip import Trip, TripStatus
from app.schemas.trip import TripCreate, TripUpdate, TripFilter, TripComplete
from app.repositories.trip import TripRepository
from app.repositories.vehicle import VehicleRepository
from app.repositories.driver import DriverRepository
from app.models.vehicle import VehicleStatus
from app.models.driver import DriverStatus
from app.models.fuel_log import FuelLog

class TripService:
    def __init__(self, trip_repo: TripRepository, vehicle_repo: VehicleRepository, driver_repo: DriverRepository):
        self.trip_repo = trip_repo
        self.vehicle_repo = vehicle_repo
        self.driver_repo = driver_repo

    def _validate_cargo_capacity(self, vehicle_id: int, cargo_weight: float):
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if vehicle and cargo_weight > vehicle.max_load_capacity_kg:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Cargo weight {cargo_weight} exceeds vehicle maximum load capacity {vehicle.max_load_capacity_kg}."
            )

    def create_trip(self, trip_in: TripCreate, created_by: int) -> Trip:
        vehicle = self.vehicle_repo.get_by_id(trip_in.vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with ID {trip_in.vehicle_id} does not exist or is deleted."
            )
            
        driver = self.driver_repo.get_by_id(trip_in.driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Driver with ID {trip_in.driver_id} does not exist or is deleted."
            )
            
        self._validate_cargo_capacity(trip_in.vehicle_id, trip_in.cargo_weight_kg)
            
        trip = Trip(**trip_in.model_dump(), created_by=created_by)
        return self.trip_repo.create(trip)

    def get_trip(self, trip_id: int) -> Trip:
        trip = self.trip_repo.get_by_id(trip_id)
        if not trip:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trip with ID {trip_id} not found."
            )
        return trip

    def list_trips(self, filters: TripFilter) -> Tuple[int, Sequence[Trip]]:
        return self.trip_repo.get_all(filters)

    def update_trip(self, trip_id: int, trip_update: TripUpdate, current_user_id: int, is_admin: bool) -> Trip:
        trip = self.get_trip(trip_id)
        
        if trip.status != TripStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only trips in DRAFT status can be updated."
            )
            
        if not is_admin and trip.created_by != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update trips that you created."
            )
            
        vid = trip_update.vehicle_id or trip.vehicle_id
        if trip_update.vehicle_id:
            vehicle = self.vehicle_repo.get_by_id(trip_update.vehicle_id)
            if not vehicle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Vehicle with ID {trip_update.vehicle_id} does not exist."
                )
                
        if trip_update.driver_id:
            driver = self.driver_repo.get_by_id(trip_update.driver_id)
            if not driver:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Driver with ID {trip_update.driver_id} does not exist."
                )

        cargo = trip_update.cargo_weight_kg or trip.cargo_weight_kg
        self._validate_cargo_capacity(vid, cargo)

        update_data = trip_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(trip, field, value)
            
        return self.trip_repo.update(trip)

    def delete_trip(self, trip_id: int) -> None:
        trip = self.get_trip(trip_id)
        
        if trip.status != TripStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Only trips in DRAFT status can be deleted."
            )
            
        self.trip_repo.delete(trip)

    def dispatch_trip(self, trip_id: int, current_user_id: int, is_admin: bool) -> Trip:
        trip = self.get_trip(trip_id)

        if trip.status != TripStatus.DRAFT:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot dispatch trip. Invalid state transition from {trip.status.value} to DISPATCHED."
            )

        if not is_admin and trip.created_by != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only dispatch trips that you created."
            )

        vehicle = self.vehicle_repo.get_by_id(trip.vehicle_id)
        if not vehicle:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle does not exist.")
        if vehicle.status != VehicleStatus.AVAILABLE:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Vehicle is not AVAILABLE.")

        driver = self.driver_repo.get_by_id(trip.driver_id)
        if not driver:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Driver does not exist.")
        if driver.status != DriverStatus.AVAILABLE:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Driver is not AVAILABLE.")
        if driver.license_expiry_date < date.today():
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Driver license is expired.")

        self._validate_cargo_capacity(trip.vehicle_id, trip.cargo_weight_kg)

        trip.status = TripStatus.DISPATCHED
        trip.dispatched_at = datetime.now(timezone.utc)
        vehicle.status = VehicleStatus.ON_TRIP
        driver.status = DriverStatus.ON_TRIP

        self.trip_repo.session.add(trip)
        self.trip_repo.session.add(vehicle)
        self.trip_repo.session.add(driver)
        self.trip_repo.session.commit()
        self.trip_repo.session.refresh(trip)
        return trip

    def complete_trip(self, trip_id: int, completion_data: TripComplete, current_user_id: int, is_admin: bool) -> Trip:
        trip = self.get_trip(trip_id)

        if trip.status != TripStatus.DISPATCHED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot complete trip. Invalid state transition from {trip.status.value} to COMPLETED."
            )

        if not is_admin and trip.created_by != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only complete trips that you created."
            )

        vehicle = self.vehicle_repo.get_by_id(trip.vehicle_id)
        driver = self.driver_repo.get_by_id(trip.driver_id)

        if completion_data.final_odometer < vehicle.odometer_km:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Final odometer ({completion_data.final_odometer}) cannot be less than current vehicle odometer ({vehicle.odometer_km})."
            )

        trip.status = TripStatus.COMPLETED
        trip.completed_at = datetime.now(timezone.utc)
        trip.final_odometer = completion_data.final_odometer
        trip.fuel_consumed_liters = completion_data.fuel_consumed_liters
        trip.revenue = completion_data.revenue

        vehicle.status = VehicleStatus.AVAILABLE
        vehicle.odometer_km = completion_data.final_odometer
        if driver:
            driver.status = DriverStatus.AVAILABLE

        fuel_log = FuelLog(
            trip_id=trip.id,
            vehicle_id=vehicle.id,
            liters=completion_data.fuel_consumed_liters
        )

        self.trip_repo.session.add(trip)
        self.trip_repo.session.add(vehicle)
        if driver:
            self.trip_repo.session.add(driver)
        self.trip_repo.session.add(fuel_log)
        self.trip_repo.session.commit()
        self.trip_repo.session.refresh(trip)
        return trip

    def cancel_trip(self, trip_id: int, current_user_id: int, is_admin: bool) -> Trip:
        trip = self.get_trip(trip_id)

        if trip.status not in [TripStatus.DRAFT, TripStatus.DISPATCHED]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot cancel trip. Invalid state transition from {trip.status.value} to CANCELLED."
            )

        if not is_admin and trip.created_by != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only cancel trips that you created."
            )

        was_dispatched = trip.status == TripStatus.DISPATCHED

        trip.status = TripStatus.CANCELLED
        trip.cancelled_at = datetime.now(timezone.utc)
        self.trip_repo.session.add(trip)

        if was_dispatched:
            vehicle = self.vehicle_repo.get_by_id(trip.vehicle_id)
            if vehicle:
                vehicle.status = VehicleStatus.AVAILABLE
                self.trip_repo.session.add(vehicle)
                
            driver = self.driver_repo.get_by_id(trip.driver_id)
            if driver:
                driver.status = DriverStatus.AVAILABLE
                self.trip_repo.session.add(driver)

        self.trip_repo.session.commit()
        self.trip_repo.session.refresh(trip)
        return trip
