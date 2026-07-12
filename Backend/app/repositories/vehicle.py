from sqlmodel import Session, select, func
from typing import Optional, Tuple, Sequence
from datetime import datetime, timezone
from app.models.vehicle import Vehicle, VehicleStatus
from app.schemas.vehicle import VehicleFilter

class VehicleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, vehicle: Vehicle) -> Vehicle:
        self.session.add(vehicle)
        self.session.commit()
        self.session.refresh(vehicle)
        return vehicle

    def get_by_id(self, vehicle_id: int) -> Optional[Vehicle]:
        statement = select(Vehicle).where(Vehicle.id == vehicle_id, Vehicle.is_deleted == False)
        return self.session.exec(statement).first()

    def get_by_registration(self, registration_number: str) -> Optional[Vehicle]:
        statement = select(Vehicle).where(
            Vehicle.registration_number == registration_number,
            Vehicle.is_deleted == False
        )
        return self.session.exec(statement).first()

    def get_all(self, filters: VehicleFilter) -> Tuple[int, Sequence[Vehicle]]:
        statement = select(Vehicle).where(Vehicle.is_deleted == False)

        if filters.status:
            statement = statement.where(Vehicle.status == filters.status)
        if filters.type:
            statement = statement.where(Vehicle.type == filters.type)
        if filters.region:
            statement = statement.where(Vehicle.region == filters.region)
        if filters.registration_search:
            statement = statement.where(Vehicle.registration_number.contains(filters.registration_search))

        # Count total
        count_stmt = select(func.count()).select_from(statement.subquery())
        total = self.session.exec(count_stmt).one()

        # Apply pagination
        statement = statement.offset(filters.skip).limit(filters.limit)
        items = self.session.exec(statement).all()

        return total, items

    def update(self, vehicle: Vehicle) -> Vehicle:
        vehicle.updated_at = datetime.now(timezone.utc)
        self.session.add(vehicle)
        self.session.commit()
        self.session.refresh(vehicle)
        return vehicle

    def retire(self, vehicle: Vehicle) -> Vehicle:
        vehicle.status = VehicleStatus.RETIRED
        vehicle.updated_at = datetime.now(timezone.utc)
        self.session.add(vehicle)
        self.session.commit()
        self.session.refresh(vehicle)
        return vehicle

    def soft_delete(self, vehicle: Vehicle) -> None:
        vehicle.is_deleted = True
        vehicle.updated_at = datetime.now(timezone.utc)
        self.session.add(vehicle)
        self.session.commit()

    def exists(self, registration_number: str) -> bool:
        vehicle = self.get_by_registration(registration_number)
        return vehicle is not None
