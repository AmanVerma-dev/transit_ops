from fastapi import HTTPException, status
from app.schemas.user import UserCreate
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def __init__(self, user_repo: UserRepository, role_repo: RoleRepository):
        self.user_repo = user_repo
        self.role_repo = role_repo

    def register_user(self, user_in: UserCreate) -> User:
        user_exists = self.user_repo.get_by_email(email=user_in.email)
        if user_exists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this email already exists in the system.",
            )
        
        role = self.role_repo.get_by_name(name="Driver")
        if not role:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Default role 'Driver' does not exist in the system.",
            )

        user = User(
            name=user_in.name,
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
            role_id=role.id,
        )
        return self.user_repo.create(user)

    def authenticate_user(self, email: str, password: str) -> dict:
        user = self.user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user"
            )
        
        role_name = user.role.name if user.role else ""
        access_token = create_access_token(subject=user.id, role=role_name)
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
