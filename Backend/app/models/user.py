from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone
from app.models.role import Role

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    password_hash: str
    role_id: Optional[int] = Field(default=None, foreign_key="role.id")
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    role: Optional[Role] = Relationship(back_populates="users")
