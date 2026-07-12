from fastapi import APIRouter
from app.api.routes import health

api_router = APIRouter()

# Register health check route
api_router.include_router(health.router, tags=["health"])
