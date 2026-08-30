"""FastAPI auth dependencies."""

from __future__ import annotations

from typing import Optional

from fastapi import Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from services.auth_service import AuthService, User, get_auth_service

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    auth: AuthService = Depends(get_auth_service),
) -> User:
    if not credentials:
        raise HTTPException(status_code=401, detail="authentication required")
    user = auth.get_user_from_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="invalid or expired token")
    return user


def get_optional_user(
    token: str = Query(""),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    auth: AuthService = Depends(get_auth_service),
) -> Optional[User]:
    if credentials:
        return auth.get_user_from_token(credentials.credentials)
    if token:
        return auth.get_user_from_token(token)
    return None


def require_roles(*roles: str):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=403,
                detail=f"role {user.role} is not allowed for this operation",
            )
        return user

    return dependency
