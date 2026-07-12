from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Any

from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_active_user, require_roles
from app.schemas.driver import (
    DriverCreate, DriverUpdate, DriverResponse, 
    DriverListResponse, DriverFilter
)
from app.models.user import User
from app.repositories.driver import DriverRepository
from app.services.driver import DriverService

router = APIRouter()

def get_driver_service(db: Session = Depends(get_db)) -> DriverService:
    return DriverService(DriverRepository(db))

@router.post(
    "",
    response_model=DriverResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new driver",
    description="Registers a new driver in the system. License number must be unique."
)
def create_driver(
    driver_in: DriverCreate,
    service: DriverService = Depends(get_driver_service),
    current_user: User = Depends(require_roles(["Safety Officer"]))
) -> Any:
    return service.create_driver(driver_in)

@router.get(
    "",
    response_model=DriverListResponse,
    summary="List all drivers",
    description="Retrieve a paginated list of drivers with optional filtering."
)
def list_drivers(
    filters: DriverFilter = Depends(),
    service: DriverService = Depends(get_driver_service),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    total, items = service.list_drivers(filters)
    return DriverListResponse(total=total, items=items)

@router.get(
    "/{driver_id}",
    response_model=DriverResponse,
    summary="Get a specific driver",
    description="Retrieve details of a driver by their ID."
)
def get_driver(
    driver_id: int,
    service: DriverService = Depends(get_driver_service),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return service.get_driver(driver_id)

@router.put(
    "/{driver_id}",
    response_model=DriverResponse,
    summary="Update a driver",
    description="Update an existing driver's details."
)
def update_driver(
    driver_id: int,
    driver_update: DriverUpdate,
    service: DriverService = Depends(get_driver_service),
    current_user: User = Depends(require_roles(["Safety Officer"]))
) -> Any:
    return service.update_driver(driver_id, driver_update)

@router.patch(
    "/{driver_id}/suspend",
    response_model=DriverResponse,
    summary="Suspend a driver",
    description="Sets the driver status to SUSPENDED."
)
def suspend_driver(
    driver_id: int,
    service: DriverService = Depends(get_driver_service),
    current_user: User = Depends(require_roles(["Safety Officer"]))
) -> Any:
    return service.suspend_driver(driver_id)

@router.patch(
    "/{driver_id}/reinstate",
    response_model=DriverResponse,
    summary="Reinstate a driver",
    description="Sets a suspended driver's status back to AVAILABLE."
)
def reinstate_driver(
    driver_id: int,
    service: DriverService = Depends(get_driver_service),
    current_user: User = Depends(require_roles(["Safety Officer"]))
) -> Any:
    return service.reinstate_driver(driver_id)

@router.delete(
    "/{driver_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a driver",
    description="Soft-deletes a driver from the system."
)
def delete_driver(
    driver_id: int,
    service: DriverService = Depends(get_driver_service),
    current_user: User = Depends(require_roles(["Safety Officer"]))
) -> None:
    service.delete_driver(driver_id)
