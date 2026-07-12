import logging
from sqlmodel import Session
from app.models.role import Role
from app.repositories.role import RoleRepository

logger = logging.getLogger("transitops.seed")

DEFAULT_ROLES = ["Fleet Manager", "Driver", "Dispatcher", "Safety Officer", "Financial Analyst"]

def seed_roles(session: Session) -> None:
    """Seed the default roles in the database."""
    role_repo = RoleRepository(session)
    for role_name in DEFAULT_ROLES:
        role = role_repo.get_by_name(role_name)
        if not role:
            new_role = Role(name=role_name)
            role_repo.create(new_role)
            logger.info(f"Role '{role_name}' created.")
        else:
            logger.info(f"Role '{role_name}' already exists.")
