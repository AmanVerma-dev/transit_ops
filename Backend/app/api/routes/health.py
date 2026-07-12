from fastapi import APIRouter
from typing import Dict

router = APIRouter()

@router.get("/health", response_model=Dict[str, str])
def get_health() -> Dict[str, str]:
    """Perform a simple health check of the backend service."""
    return {
        "status": "healthy",
        "service": "TransitOps Backend",
        "version": "1.0.0"
    }
