from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Any

from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_active_user, require_roles
from app.schemas.trip import (
    TripCreate, TripUpdate, TripResponse, 
    TripListResponse, TripFilter, TripComplete
)
from app.models.user import User
from app.repositories.trip import TripRepository
from app.repositories.vehicle import VehicleRepository
from app.repositories.driver import DriverRepository
from app.services.trip import TripService

router = APIRouter()

def get_trip_service(db: Session = Depends(get_db)) -> TripService:
    return TripService(
        TripRepository(db),
        VehicleRepository(db),
        DriverRepository(db)
    )

@router.post(
    "",
    response_model=TripResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new trip",
    description="Registers a new trip in the system. The trip will start in DRAFT status."
)
def create_trip(
    trip_in: TripCreate,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Driver"]))
) -> Any:
    return service.create_trip(trip_in, created_by=current_user.id)

@router.get(
    "",
    response_model=TripListResponse,
    summary="List all trips",
    description="Retrieve a paginated list of trips with optional filtering."
)
def list_trips(
    filters: TripFilter = Depends(),
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    total, items = service.list_trips(filters)
    return TripListResponse(total=total, items=items)

@router.get(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Get a specific trip",
    description="Retrieve details of a trip by its ID."
)
def get_trip(
    trip_id: int,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    return service.get_trip(trip_id)

@router.put(
    "/{trip_id}",
    response_model=TripResponse,
    summary="Update a trip",
    description="Update an existing trip. Only DRAFT trips can be updated."
)
def update_trip(
    trip_id: int,
    trip_update: TripUpdate,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Driver"]))
) -> Any:
    user_role = current_user.role.name if current_user.role else ""
    is_admin = user_role == "Fleet Manager"
    return service.update_trip(trip_id, trip_update, current_user.id, is_admin)

@router.delete(
    "/{trip_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a trip",
    description="Permanently deletes a trip. Only DRAFT trips can be deleted."
)
def delete_trip(
    trip_id: int,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(require_roles(["Fleet Manager"]))
) -> None:
    service.delete_trip(trip_id)

@router.patch(
    "/{trip_id}/dispatch",
    response_model=TripResponse,
    summary="Dispatch a trip",
    description="Transitions a DRAFT trip to DISPATCHED status."
)
def dispatch_trip(
    trip_id: int,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Driver"]))
) -> Any:
    user_role = current_user.role.name if current_user.role else ""
    is_admin = user_role == "Fleet Manager"
    return service.dispatch_trip(trip_id, current_user.id, is_admin)

@router.patch(
    "/{trip_id}/complete",
    response_model=TripResponse,
    summary="Complete a trip",
    description="Transitions a DISPATCHED trip to COMPLETED status with final metrics."
)
def complete_trip(
    trip_id: int,
    completion_data: TripComplete,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Driver"]))
) -> Any:
    user_role = current_user.role.name if current_user.role else ""
    is_admin = user_role == "Fleet Manager"
    return service.complete_trip(trip_id, completion_data, current_user.id, is_admin)

@router.patch(
    "/{trip_id}/cancel",
    response_model=TripResponse,
    summary="Cancel a trip",
    description="Transitions a DRAFT or DISPATCHED trip to CANCELLED status."
)
def cancel_trip(
    trip_id: int,
    service: TripService = Depends(get_trip_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Driver"]))
) -> Any:
    user_role = current_user.role.name if current_user.role else ""
    is_admin = user_role == "Fleet Manager"
    return service.cancel_trip(trip_id, current_user.id, is_admin)
