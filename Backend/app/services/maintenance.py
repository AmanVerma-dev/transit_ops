from fastapi import HTTPException, status
from typing import Tuple, Sequence, Optional
from datetime import datetime, timezone
from app.models.maintenance import Maintenance, MaintenanceStatus
from app.schemas.maintenance import MaintenanceCreate, MaintenanceUpdate, MaintenanceFilter
from app.repositories.maintenance import MaintenanceRepository
from app.repositories.vehicle import VehicleRepository

class MaintenanceService:
    def __init__(self, maintenance_repo: MaintenanceRepository, vehicle_repo: VehicleRepository):
        self.maintenance_repo = maintenance_repo
        self.vehicle_repo = vehicle_repo

    def schedule_maintenance(self, maintenance_in: MaintenanceCreate, created_by: int) -> Maintenance:
        # Validate vehicle exists and is not deleted
        vehicle = self.vehicle_repo.get_by_id(maintenance_in.vehicle_id)
        if not vehicle:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Vehicle with ID {maintenance_in.vehicle_id} not found."
            )
        
        maintenance = Maintenance(
            **maintenance_in.model_dump(),
            created_by=created_by,
            status=MaintenanceStatus.SCHEDULED
        )
        return self.maintenance_repo.create(maintenance)

    def get_maintenance(self, maintenance_id: int) -> Maintenance:
        maintenance = self.maintenance_repo.get_by_id(maintenance_id)
        if not maintenance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Maintenance record with ID {maintenance_id} not found."
            )
        return maintenance

    def list_maintenance(self, filters: MaintenanceFilter) -> Tuple[int, Sequence[Maintenance]]:
        return self.maintenance_repo.get_all(filters)

    def update_maintenance(self, maintenance_id: int, maintenance_update: MaintenanceUpdate) -> Maintenance:
        maintenance = self.get_maintenance(maintenance_id)
        
        # Only SCHEDULED maintenance can be updated with all fields
        if maintenance.status != MaintenanceStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Only SCHEDULED maintenance can be updated. Current status: {maintenance.status}"
            )
        
        update_data = maintenance_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(maintenance, field, value)
            
        return self.maintenance_repo.update(maintenance)

    def start_maintenance(self, maintenance_id: int, technician_notes: Optional[str] = None) -> Maintenance:
        maintenance = self.get_maintenance(maintenance_id)
        
        # Validate state transition: Only SCHEDULED can become IN_PROGRESS
        if maintenance.status != MaintenanceStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot start maintenance. Only SCHEDULED maintenance can be started. Current status: {maintenance.status}"
            )
        
        maintenance.status = MaintenanceStatus.IN_PROGRESS
        maintenance.started_at = datetime.now(timezone.utc)
        if technician_notes:
            maintenance.technician_notes = technician_notes
        
        return self.maintenance_repo.update(maintenance)

    def complete_maintenance(self, maintenance_id: int, actual_cost: float, technician_notes: Optional[str] = None) -> Maintenance:
        maintenance = self.get_maintenance(maintenance_id)
        
        # Validate state transition: Only IN_PROGRESS can become COMPLETED
        if maintenance.status != MaintenanceStatus.IN_PROGRESS:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot complete maintenance. Only IN_PROGRESS maintenance can be completed. Current status: {maintenance.status}"
            )
        
        # Validate actual cost
        if actual_cost < 0:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Actual cost must be greater than or equal to 0."
            )
        
        maintenance.status = MaintenanceStatus.COMPLETED
        maintenance.completed_at = datetime.now(timezone.utc)
        maintenance.actual_cost = actual_cost
        if technician_notes:
            maintenance.technician_notes = technician_notes
        
        return self.maintenance_repo.update(maintenance)

    def cancel_maintenance(self, maintenance_id: int, reason: Optional[str] = None) -> Maintenance:
        maintenance = self.get_maintenance(maintenance_id)
        
        # Validate state transition: Only SCHEDULED can become CANCELLED
        if maintenance.status != MaintenanceStatus.SCHEDULED:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot cancel maintenance. Only SCHEDULED maintenance can be cancelled. Current status: {maintenance.status}"
            )
        
        maintenance.status = MaintenanceStatus.CANCELLED
        if reason:
            maintenance.technician_notes = f"CANCELLED: {reason}"
        
        return self.maintenance_repo.update(maintenance)

    def delete_maintenance(self, maintenance_id: int) -> None:
        maintenance = self.get_maintenance(maintenance_id)
        self.maintenance_repo.delete(maintenance)
