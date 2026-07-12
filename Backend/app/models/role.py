from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional
from datetime import datetime

class Role(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)

    users: List["User"] = Relationship(back_populates="role")
