from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlmodel import Session
from pydantic import ValidationError

from app.core.config import settings
from app.api.dependencies import get_db
from app.models.user import User
from app.schemas.auth import TokenPayload
from app.repositories.user import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login" if settings.API_V1_STR else "/auth/login")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id=int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def require_roles(roles: list[str]):
    def role_checker(current_user: User = Depends(get_current_active_user)):
        user_role = current_user.role.name if current_user.role else ""
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role"
            )
        return current_user
    return role_checker
