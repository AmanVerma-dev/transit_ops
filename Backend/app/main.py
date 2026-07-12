from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.logging import setup_logging
from app.api.router import api_router

# Initialize system logging configuration
setup_logging()
logger = logging.getLogger("transitops")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=(
        "TransitOps is a smart transport operations platform providing fleet management, "
        "driver management, trip lifecycle, maintenance scheduling, fuel tracking, "
        "analytics, and real-time dashboards through a RESTful API."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "health", "description": "Service health check"},
        {"name": "auth", "description": "Authentication & JWT token management"},
        {"name": "vehicles", "description": "Vehicle fleet CRUD operations"},
        {"name": "drivers", "description": "Driver management & lifecycle"},
        {"name": "trips", "description": "Trip creation, lifecycle & business rules"},
        {"name": "maintenance", "description": "Maintenance scheduling & tracking"},
        {"name": "analytics", "description": "Fleet analytics & reporting"},
        {"name": "reports", "description": "CSV data exports"},
        {"name": "dashboard", "description": "Real-time operational dashboards"},
    ],
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register master router
app.include_router(api_router)

from app.core.database import init_db, engine
from sqlmodel import Session
from app.seed.roles import seed_roles
from app.seed.users import seed_users
from app.seed.demo_data import seed_demo_data

@app.on_event("startup")
def on_startup() -> None:
    logger.info("Initializing database schemas...")
    init_db()
    
    logger.info("Seeding initial data...")
    with Session(engine) as session:
        seed_roles(session)
        seed_users(session)
        seed_demo_data(session)

    logger.info("TransitOps Backend service started successfully.")

