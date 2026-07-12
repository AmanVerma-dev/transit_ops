from fastapi import APIRouter
from app.api.routes import health, auth, vehicles

api_router = APIRouter()

# Register routes
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(vehicles.router, prefix="/vehicles", tags=["vehicles"])
