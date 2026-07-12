from fastapi import HTTPException, status
from typing import Tuple, Sequence
from datetime import date
from app.models.driver import Driver, DriverStatus
from app.schemas.driver import DriverCreate, DriverUpdate, DriverFilter
from app.repositories.driver import DriverRepository

class DriverService:
    def __init__(self, driver_repo: DriverRepository):
        self.driver_repo = driver_repo

    def create_driver(self, driver_in: DriverCreate) -> Driver:
        if self.driver_repo.exists(driver_in.license_number):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Driver with license number '{driver_in.license_number}' already exists."
            )
            
        driver = Driver(**driver_in.model_dump())
        return self.driver_repo.create(driver)

    def get_driver(self, driver_id: int) -> Driver:
        driver = self.driver_repo.get_by_id(driver_id)
        if not driver:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Driver with ID {driver_id} not found."
            )
        return driver

    def list_drivers(self, filters: DriverFilter) -> Tuple[int, Sequence[Driver]]:
        return self.driver_repo.get_all(filters)

    def update_driver(self, driver_id: int, driver_update: DriverUpdate) -> Driver:
        driver = self.get_driver(driver_id)
        
        update_data = driver_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(driver, field, value)
            
        return self.driver_repo.update(driver)

    def suspend_driver(self, driver_id: int) -> Driver:
        driver = self.get_driver(driver_id)
        if driver.status == DriverStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver is already suspended."
            )
        return self.driver_repo.suspend(driver)

    def reinstate_driver(self, driver_id: int) -> Driver:
        driver = self.get_driver(driver_id)
        if driver.status != DriverStatus.SUSPENDED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only suspended drivers can be reinstated."
            )
        return self.driver_repo.reinstate(driver)

    def delete_driver(self, driver_id: int) -> None:
        driver = self.get_driver(driver_id)
        self.driver_repo.soft_delete(driver)
