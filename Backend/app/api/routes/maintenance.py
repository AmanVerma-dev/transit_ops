from fastapi import APIRouter, Depends, status, Body
from sqlmodel import Session
from typing import Any

from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_active_user, require_roles
from app.schemas.maintenance import (
    MaintenanceCreate, MaintenanceUpdate, MaintenanceResponse,
    MaintenanceListResponse, MaintenanceFilter
)
from app.models.user import User
from app.repositories.maintenance import MaintenanceRepository
from app.repositories.vehicle import VehicleRepository
from app.services.maintenance import MaintenanceService

router = APIRouter()

def get_maintenance_service(db: Session = Depends(get_db)) -> MaintenanceService:
    return MaintenanceService(MaintenanceRepository(db), VehicleRepository(db))

@router.post(
    "",
    response_model=MaintenanceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Schedule maintenance",
    description="Schedule a new maintenance record for a vehicle. Vehicle must exist and not be deleted."
)
def schedule_maintenance(
    maintenance_in: MaintenanceCreate,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Safety Officer"]))
) -> Any:
    """
    Schedule maintenance for a vehicle.
    
    **Permissions:** Fleet Manager, Safety Officer
    
    **Example Request:**
    ```json
    {
        "vehicle_id": 1,
        "maintenance_type": "Preventive",
        "description": "Regular oil change and filter replacement",
        "scheduled_date": "2026-07-20T10:00:00Z",
        "estimated_cost": 150.00,
        "technician_notes": "Check brake pads while servicing"
    }
    ```
    
    **Returns:** The created maintenance record with status SCHEDULED
    """
    return service.schedule_maintenance(maintenance_in, current_user.id)

@router.get(
    "",
    response_model=MaintenanceListResponse,
    summary="List all maintenance records",
    description="Retrieve a paginated list of maintenance records with optional filtering by vehicle, status, type, and date range."
)
def list_maintenance(
    filters: MaintenanceFilter = Depends(),
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    List maintenance records with filtering and pagination.
    
    **Filters:**
    - vehicle_id: Filter by specific vehicle
    - status: SCHEDULED, IN_PROGRESS, COMPLETED, CANCELLED
    - maintenance_type: Preventive, Corrective, Emergency, Inspection
    - scheduled_date: Exact date match
    - start_date & end_date: Date range filter
    - skip & limit: Pagination
    
    **Returns:** Paginated list of maintenance records
    """
    total, items = service.list_maintenance(filters)
    return MaintenanceListResponse(total=total, items=items)

@router.get(
    "/{maintenance_id}",
    response_model=MaintenanceResponse,
    summary="Get maintenance record",
    description="Retrieve details of a specific maintenance record by ID."
)
def get_maintenance(
    maintenance_id: int,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(get_current_active_user)
) -> Any:
    """
    Get a specific maintenance record.
    
    **Returns:** Maintenance record details
    
    **Status Codes:**
    - 200: Success
    - 404: Maintenance record not found
    """
    return service.get_maintenance(maintenance_id)

@router.put(
    "/{maintenance_id}",
    response_model=MaintenanceResponse,
    summary="Update maintenance record",
    description="Update a SCHEDULED maintenance record. Only SCHEDULED maintenance can be updated."
)
def update_maintenance(
    maintenance_id: int,
    maintenance_update: MaintenanceUpdate,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Safety Officer"]))
) -> Any:
    """
    Update a scheduled maintenance record.
    
    **Permissions:** Fleet Manager, Safety Officer
    
    **Business Rules:**
    - Only SCHEDULED maintenance can be updated
    - Returns 409 Conflict if maintenance is not in SCHEDULED status
    
    **Status Codes:**
    - 200: Success
    - 404: Maintenance record not found
    - 409: Invalid state transition
    """
    return service.update_maintenance(maintenance_id, maintenance_update)

@router.patch(
    "/{maintenance_id}/start",
    response_model=MaintenanceResponse,
    summary="Start maintenance",
    description="Transition maintenance from SCHEDULED to IN_PROGRESS. Records the start time."
)
def start_maintenance(
    maintenance_id: int,
    technician_notes: str = Body(None, embed=True),
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Safety Officer"]))
) -> Any:
    """
    Start a scheduled maintenance.
    
    **Permissions:** Fleet Manager, Safety Officer
    
    **State Transition:** SCHEDULED → IN_PROGRESS
    
    **Business Rules:**
    - Only SCHEDULED maintenance can be started
    - Sets started_at timestamp
    - Optional technician notes
    
    **Example Request:**
    ```json
    {
        "technician_notes": "Starting oil change service"
    }
    ```
    
    **Status Codes:**
    - 200: Success
    - 404: Maintenance record not found
    - 409: Invalid state transition (not SCHEDULED)
    """
    return service.start_maintenance(maintenance_id, technician_notes)

@router.patch(
    "/{maintenance_id}/complete",
    response_model=MaintenanceResponse,
    summary="Complete maintenance",
    description="Transition maintenance from IN_PROGRESS to COMPLETED. Records actual cost and completion time."
)
def complete_maintenance(
    maintenance_id: int,
    actual_cost: float = Body(..., ge=0, embed=True),
    technician_notes: str = Body(None, embed=True),
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Safety Officer"]))
) -> Any:
    """
    Complete an in-progress maintenance.
    
    **Permissions:** Fleet Manager, Safety Officer
    
    **State Transition:** IN_PROGRESS → COMPLETED
    
    **Business Rules:**
    - Only IN_PROGRESS maintenance can be completed
    - Actual cost must be >= 0
    - Sets completed_at timestamp
    - Optional technician notes
    
    **Example Request:**
    ```json
    {
        "actual_cost": 175.50,
        "technician_notes": "Oil change completed. Brake pads at 60% - good condition."
    }
    ```
    
    **Status Codes:**
    - 200: Success
    - 404: Maintenance record not found
    - 409: Invalid state transition (not IN_PROGRESS)
    - 422: Invalid actual cost
    """
    return service.complete_maintenance(maintenance_id, actual_cost, technician_notes)

@router.patch(
    "/{maintenance_id}/cancel",
    response_model=MaintenanceResponse,
    summary="Cancel maintenance",
    description="Transition maintenance from SCHEDULED to CANCELLED. Only scheduled maintenance can be cancelled."
)
def cancel_maintenance(
    maintenance_id: int,
    reason: str = Body(None, embed=True),
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(require_roles(["Fleet Manager", "Safety Officer"]))
) -> Any:
    """
    Cancel a scheduled maintenance.
    
    **Permissions:** Fleet Manager, Safety Officer
    
    **State Transition:** SCHEDULED → CANCELLED
    
    **Business Rules:**
    - Only SCHEDULED maintenance can be cancelled
    - Optional cancellation reason
    
    **Example Request:**
    ```json
    {
        "reason": "Vehicle sold, maintenance no longer needed"
    }
    ```
    
    **Status Codes:**
    - 200: Success
    - 404: Maintenance record not found
    - 409: Invalid state transition (not SCHEDULED)
    """
    return service.cancel_maintenance(maintenance_id, reason)

@router.delete(
    "/{maintenance_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete maintenance record",
    description="Permanently delete a maintenance record from the system."
)
def delete_maintenance(
    maintenance_id: int,
    service: MaintenanceService = Depends(get_maintenance_service),
    current_user: User = Depends(require_roles(["Fleet Manager"]))
) -> None:
    """
    Delete a maintenance record.
    
    **Permissions:** Fleet Manager only
    
    **Status Codes:**
    - 204: Success (no content)
    - 404: Maintenance record not found
    """
    service.delete_maintenance(maintenance_id)
