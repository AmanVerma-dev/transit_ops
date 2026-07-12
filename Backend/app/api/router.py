from fastapi import APIRouter
from app.api.routes import health, auth, vehicles, drivers, trips, maintenance, dashboard
from app.api.routes.analytics import analytics_router, reports_router

api_router = APIRouter()

# Register routes
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["drivers"])
api_router.include_router(trips.router, prefix="/trips", tags=["trips"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["maintenance"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
api_router.include_router(reports_router, prefix="/reports", tags=["reports"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
