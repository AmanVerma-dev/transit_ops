from sqlmodel import Session, select, func
from typing import Optional, Tuple, Sequence
from datetime import datetime, timezone
from app.models.maintenance import Maintenance, MaintenanceStatus
from app.schemas.maintenance import MaintenanceFilter

class MaintenanceRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, maintenance: Maintenance) -> Maintenance:
        self.session.add(maintenance)
        self.session.commit()
        self.session.refresh(maintenance)
        return maintenance

    def get_by_id(self, maintenance_id: int) -> Optional[Maintenance]:
        statement = select(Maintenance).where(Maintenance.id == maintenance_id)
        return self.session.exec(statement).first()

    def get_all(self, filters: MaintenanceFilter) -> Tuple[int, Sequence[Maintenance]]:
        statement = select(Maintenance)

        if filters.vehicle_id:
            statement = statement.where(Maintenance.vehicle_id == filters.vehicle_id)
        if filters.status:
            statement = statement.where(Maintenance.status == filters.status)
        if filters.maintenance_type:
            statement = statement.where(Maintenance.maintenance_type == filters.maintenance_type)
        if filters.scheduled_date:
            statement = statement.where(Maintenance.scheduled_date == filters.scheduled_date)
        if filters.start_date:
            statement = statement.where(Maintenance.scheduled_date >= filters.start_date)
        if filters.end_date:
            statement = statement.where(Maintenance.scheduled_date <= filters.end_date)

        # Count total
        count_stmt = select(func.count()).select_from(statement.subquery())
        total = self.session.exec(count_stmt).one()

        # Apply pagination and ordering
        statement = statement.order_by(Maintenance.scheduled_date.desc()).offset(filters.skip).limit(filters.limit)
        items = self.session.exec(statement).all()

        return total, items

    def update(self, maintenance: Maintenance) -> Maintenance:
        maintenance.updated_at = datetime.now(timezone.utc)
        self.session.add(maintenance)
        self.session.commit()
        self.session.refresh(maintenance)
        return maintenance

    def delete(self, maintenance: Maintenance) -> None:
        self.session.delete(maintenance)
        self.session.commit()

    def exists(self, maintenance_id: int) -> bool:
        maintenance = self.get_by_id(maintenance_id)
        return maintenance is not None

    def has_active_maintenance(self, vehicle_id: int) -> bool:
        """Check if a vehicle has any SCHEDULED or IN_PROGRESS maintenance."""
        statement = select(Maintenance).where(
            Maintenance.vehicle_id == vehicle_id,
            Maintenance.status.in_([MaintenanceStatus.SCHEDULED, MaintenanceStatus.IN_PROGRESS])
        )
        return self.session.exec(statement).first() is not None
