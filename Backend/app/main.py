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
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

@app.on_event("startup")
def on_startup() -> None:
    logger.info("Initializing database schemas...")
    init_db()
    
    logger.info("Seeding initial data...")
    with Session(engine) as session:
        seed_roles(session)
        seed_users(session)

    logger.info("TransitOps Backend service started successfully.")
