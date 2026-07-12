from sqlmodel import Session, select, func
from typing import Optional, Tuple, Sequence
from datetime import datetime, timezone
from app.models.trip import Trip, TripStatus
from app.schemas.trip import TripFilter

class TripRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, trip: Trip) -> Trip:
        self.session.add(trip)
        self.session.commit()
        self.session.refresh(trip)
        return trip

    def get_by_id(self, trip_id: int) -> Optional[Trip]:
        return self.session.get(Trip, trip_id)

    def exists(self, trip_id: int) -> bool:
        return self.get_by_id(trip_id) is not None

    def get_all(self, filters: TripFilter) -> Tuple[int, Sequence[Trip]]:
        statement = select(Trip)

        if filters.status:
            statement = statement.where(Trip.status == filters.status)
        if filters.vehicle_id:
            statement = statement.where(Trip.vehicle_id == filters.vehicle_id)
        if filters.driver_id:
            statement = statement.where(Trip.driver_id == filters.driver_id)
        if filters.created_by:
            statement = statement.where(Trip.created_by == filters.created_by)
        if filters.start_date:
            statement = statement.where(Trip.created_at >= datetime.combine(filters.start_date, datetime.min.time(), tzinfo=timezone.utc))
        if filters.end_date:
            statement = statement.where(Trip.created_at <= datetime.combine(filters.end_date, datetime.max.time(), tzinfo=timezone.utc))

        # Count total
        count_stmt = select(func.count()).select_from(statement.subquery())
        total = self.session.exec(count_stmt).one()

        # Apply pagination
        statement = statement.order_by(Trip.created_at.desc()).offset(filters.skip).limit(filters.limit)
        items = self.session.exec(statement).all()

        return total, items

    def update(self, trip: Trip) -> Trip:
        trip.updated_at = datetime.now(timezone.utc)
        self.session.add(trip)
        self.session.commit()
        self.session.refresh(trip)
        return trip

    def delete(self, trip: Trip) -> None:
        self.session.delete(trip)
        self.session.commit()
