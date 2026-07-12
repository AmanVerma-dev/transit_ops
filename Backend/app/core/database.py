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
    # Tables will be generated from metadata imports once models are defined in Phase 1
    # SQLModel.metadata.create_all(engine)
    pass
