import logging
from sqlmodel import Session
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.core.security import get_password_hash

logger = logging.getLogger("transitops.seed")

DEFAULT_USERS = [
    {
        "name": "Admin Manager",
        "email": "manager@transitops.com",
        "password": "password123",
        "role_name": "Fleet Manager"
    },
    {
        "name": "John Driver",
        "email": "driver@transitops.com",
        "password": "password123",
        "role_name": "Driver"
    },
    {
        "name": "Sarah Safety",
        "email": "safety@transitops.com",
        "password": "password123",
        "role_name": "Safety Officer"
    },
    {
        "name": "Finance Bob",
        "email": "finance@transitops.com",
        "password": "password123",
        "role_name": "Financial Analyst"
    }
]

def seed_users(session: Session) -> None:
    """Seed the default users in the database."""
    user_repo = UserRepository(session)
    role_repo = RoleRepository(session)
    
    for user_data in DEFAULT_USERS:
        user = user_repo.get_by_email(user_data["email"])
        if not user:
            role = role_repo.get_by_name(user_data["role_name"])
            if role:
                new_user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    password_hash=get_password_hash(user_data["password"]),
                    role_id=role.id
                )
                user_repo.create(new_user)
                logger.info(f"User '{user_data['email']}' created.")
            else:
                logger.error(f"Cannot create user: Role '{user_data['role_name']}' not found.")
        else:
            logger.info(f"User '{user_data['email']}' already exists.")
