from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Any

from app.api.dependencies import get_db
from app.api.dependencies.auth import get_current_active_user
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token
from app.models.user import User
from app.repositories.user import UserRepository
from app.repositories.role import RoleRepository
from app.services.auth import AuthService

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db)
) -> Any:
    """Register a new user."""
    auth_service = AuthService(UserRepository(db), RoleRepository(db))
    return auth_service.register_user(user_in)

@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    auth_service = AuthService(UserRepository(db), RoleRepository(db))
    return auth_service.authenticate_user(email=form_data.username, password=form_data.password)

@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """Get current user details."""
    return current_user
