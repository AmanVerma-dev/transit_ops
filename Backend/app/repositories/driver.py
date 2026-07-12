from sqlmodel import Session, select, func
from typing import Optional, Tuple, Sequence
from datetime import datetime, date, timezone
from app.models.driver import Driver, DriverStatus
from app.schemas.driver import DriverFilter

class DriverRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, driver: Driver) -> Driver:
        self.session.add(driver)
        self.session.commit()
        self.session.refresh(driver)
        return driver

    def get_by_id(self, driver_id: int) -> Optional[Driver]:
        statement = select(Driver).where(Driver.id == driver_id, Driver.is_deleted == False)
        return self.session.exec(statement).first()

    def get_by_license(self, license_number: str) -> Optional[Driver]:
        statement = select(Driver).where(
            Driver.license_number == license_number,
            Driver.is_deleted == False
        )
        return self.session.exec(statement).first()

    def exists(self, license_number: str) -> bool:
        statement = select(Driver).where(Driver.license_number == license_number)
        return self.session.exec(statement).first() is not None

    def get_all(self, filters: DriverFilter) -> Tuple[int, Sequence[Driver]]:
        statement = select(Driver).where(Driver.is_deleted == False)

        if filters.status:
            statement = statement.where(Driver.status == filters.status)
        if filters.license_category:
            statement = statement.where(Driver.license_category == filters.license_category)
        if filters.search_name:
            statement = statement.where(Driver.name.contains(filters.search_name))
        if filters.search_license:
            statement = statement.where(Driver.license_number.contains(filters.search_license))
        if filters.expired_license is not None:
            today = date.today()
            if filters.expired_license:
                statement = statement.where(Driver.license_expiry_date < today)
            else:
                statement = statement.where(Driver.license_expiry_date >= today)

        # Count total
        count_stmt = select(func.count()).select_from(statement.subquery())
        total = self.session.exec(count_stmt).one()

        # Apply pagination
        statement = statement.order_by(Driver.created_at.desc()).offset(filters.skip).limit(filters.limit)
        items = self.session.exec(statement).all()

        return total, items

    def update(self, driver: Driver) -> Driver:
        driver.updated_at = datetime.now(timezone.utc)
        self.session.add(driver)
        self.session.commit()
        self.session.refresh(driver)
        return driver

    def suspend(self, driver: Driver) -> Driver:
        driver.status = DriverStatus.SUSPENDED
        driver.updated_at = datetime.now(timezone.utc)
        self.session.add(driver)
        self.session.commit()
        self.session.refresh(driver)
        return driver

    def reinstate(self, driver: Driver) -> Driver:
        driver.status = DriverStatus.AVAILABLE
        driver.updated_at = datetime.now(timezone.utc)
        self.session.add(driver)
        self.session.commit()
        self.session.refresh(driver)
        return driver

    def soft_delete(self, driver: Driver) -> None:
        driver.is_deleted = True
        driver.updated_at = datetime.now(timezone.utc)
        self.session.add(driver)
        self.session.commit()
