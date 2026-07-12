from typing import Generator
from sqlmodel import Session
from app.core.database import engine

def get_db() -> Generator[Session, None, None]:
    """Provide a database session dependency for API route handlers."""
    with Session(engine) as session:
        yield session
