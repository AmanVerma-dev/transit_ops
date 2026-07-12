from sqlmodel import create_engine, SQLModel
from app.core.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True
)

def init_db() -> None:
    """Initialize database schemas (useful for Phase 0 checks and test setups)."""
    # Import all models before creating tables so metadata is populated
    from app.models import role, user, vehicle, driver, trip, maintenance, fuel_log
    SQLModel.metadata.create_all(engine)
