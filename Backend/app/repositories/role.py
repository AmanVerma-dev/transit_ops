from sqlmodel import Session, select
from typing import Optional
from app.models.role import Role

class RoleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_name(self, name: str) -> Optional[Role]:
        statement = select(Role).where(Role.name == name)
        return self.session.exec(statement).first()

    def create(self, role: Role) -> Role:
        self.session.add(role)
        self.session.commit()
        self.session.refresh(role)
        return role
