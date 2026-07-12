from fastapi import HTTPException, status
from typing import Tuple, Sequence
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleFilter
from app.repositories.vehicle import VehicleRepository

class VehicleService:
    def __init__(self, vehicle_repo: VehicleRepository):
        self.vehicle_repo = vehicle_repo

    def create_vehicle(self, vehicle_in: VehicleCreate) -> Vehicle:
        if self.vehicle_repo.exists(vehicle_in.registration_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Vehicle with registration number '{vehicle_in.registration_number}' already exists."
            )
        
        vehicle = Vehicle(**vehicle_in.model_dump())
        return self.vehicle_repo.create(vehicle)

    def get_vehicle(self, vehicle_id: int) -> Vehicle:
        vehicle = self.vehicle_repo.get_by_id(vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with ID {vehicle_id} not found."
            )
        return vehicle

    def list_vehicles(self, filters: VehicleFilter) -> Tuple[int, Sequence[Vehicle]]:
        return self.vehicle_repo.get_all(filters)

    def update_vehicle(self, vehicle_id: int, vehicle_update: VehicleUpdate) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)
        
        update_data = vehicle_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(vehicle, field, value)
            
        return self.vehicle_repo.update(vehicle)

    def retire_vehicle(self, vehicle_id: int) -> Vehicle:
        vehicle = self.get_vehicle(vehicle_id)
        return self.vehicle_repo.retire(vehicle)

    def delete_vehicle(self, vehicle_id: int) -> None:
        vehicle = self.get_vehicle(vehicle_id)
        self.vehicle_repo.soft_delete(vehicle)
