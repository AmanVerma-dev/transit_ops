from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Any

from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_active_user, require_roles
from app.schemas.vehicle import (
    VehicleCreate, VehicleUpdate, VehicleResponse, 
    VehicleListResponse, VehicleFilter
)
from app.models.user import User
from app.repositories.vehicle import VehicleRepository
from app.services.vehicle import VehicleService

router = APIRouter()

def get_vehicle_service(db: Session = Depends(get_db)) -> VehicleService:
    return VehicleService(VehicleRepository(db))

@router.post(
    "",
    response_model=VehicleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vehicle",
    description="Registers a new vehicle in the system. Registration number must be unique."
)
def create_vehicle(
    vehicle_in: VehicleCreate,
    service: VehicleService = Depends(get_vehicle_service),
    current_user: User = Depends(require_roles(["Fleet Manager"]))
) -> Any:
    return service.create_vehicle(vehicle_in)

@router.get(
    "",
    response_model=VehicleListResponse,
    summary="List all vehicles",
    description="Retrieve a paginated list of vehicles with optional filtering."
)
def list_vehicles(
    filters: VehicleFilter = Depends(),
    service: VehicleService = Depends(get_vehicle_service),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    total, items = service.list_vehicles(filters)
    return VehicleListResponse(total=total, items=items)

@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Get a specific vehicle",
    description="Retrieve details of a vehicle by its ID."
)
def get_vehicle(
    vehicle_id: int,
    service: VehicleService = Depends(get_vehicle_service),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return service.get_vehicle(vehicle_id)

@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse,
    summary="Update a vehicle",
    description="Update an existing vehicle's details."
)
def update_vehicle(
    vehicle_id: int,
    vehicle_update: VehicleUpdate,
    service: VehicleService = Depends(get_vehicle_service),
    current_user: User = Depends(require_roles(["Fleet Manager"]))
) -> Any:
    return service.update_vehicle(vehicle_id, vehicle_update)

@router.patch(
    "/{vehicle_id}/retire",
    response_model=VehicleResponse,
    summary="Retire a vehicle",
    description="Sets the vehicle status to RETIRED. It will no longer be available for dispatch."
)
def retire_vehicle(
    vehicle_id: int,
    service: VehicleService = Depends(get_vehicle_service),
    current_user: User = Depends(require_roles(["Fleet Manager"]))
) -> Any:
    return service.retire_vehicle(vehicle_id)

@router.delete(
    "/{vehicle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vehicle",
    description="Soft-deletes a vehicle from the system. It will no longer appear in normal queries."
)
def delete_vehicle(
    vehicle_id: int,
    service: VehicleService = Depends(get_vehicle_service),
    current_user: User = Depends(require_roles(["Fleet Manager"]))
) -> None:
    service.delete_vehicle(vehicle_id)
