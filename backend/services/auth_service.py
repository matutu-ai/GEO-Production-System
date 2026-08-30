"""Simple JWT auth service with JSON-backed users."""

from __future__ import annotations

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import jwt

from config.settings import JWT_ALGORITHM, JWT_EXPIRE_MINUTES, JWT_SECRET
from database.repositories import load_user_records

ROLE_RANK = {
    "CLIENT": 1,
    "MEMBER": 2,
    "MANAGER": 3,
    "ADMIN": 4,
}

logger = logging.getLogger(__name__)


class User:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.id = str(data.get("id") or "")
        self.username = str(data.get("username") or "")
        self.role = str(data.get("role") or "CLIENT")
        self.display_name = str(data.get("display_name") or self.username)
        self.created_time = data.get("created_time", "")
        self.password_hash = data.get("password_hash", "")

    @property
    def role_rank(self) -> int:
        return ROLE_RANK.get(self.role, 0)

    def to_public_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "username": self.username,
            "role": self.role,
            "display_name": self.display_name,
            "created_time": self.created_time,
        }

    def to_token_dict(self) -> Dict[str, Any]:
        return {
            "sub": self.id,
            "username": self.username,
            "role": self.role,
            "display_name": self.display_name,
        }


class AuthService:
    def __init__(self) -> None:
        self.users: Dict[str, User] = {}
        self._load()

    def _load(self) -> None:
        for item in load_user_records():
            user = User(item)
            if user.id:
                self.users[user.id] = user

    def authenticate(self, username: str, password: str) -> Optional[User]:
        target = next(
            (
                user
                for user in self.users.values()
                if user.username == username
            ),
            None,
        )
        if not target:
            return None
        password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
        if password_hash != target.password_hash:
            return None
        return target

    def create_token(self, user: User) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            **user.to_token_dict(),
            "iat": now,
            "exp": now + timedelta(minutes=JWT_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        try:
            return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            logger.warning(
                "JWT rejected: expired, token_prefix=%s",
                token[:12] if isinstance(token, str) else "non-string",
            )
            return None
        except jwt.PyJWTError as exc:
            logger.warning(
                "JWT rejected: invalid, token_prefix=%s, reason=%s",
                token[:12] if isinstance(token, str) else "non-string",
                exc,
            )
            return None

    def get_user_from_token(self, token: str) -> Optional[User]:
        payload = self.decode_token(token)
        if not payload:
            return None
        user_id = str(payload.get("sub", ""))
        user = self.users.get(user_id)
        if not user:
            logger.warning("JWT rejected: user not found, sub=%s", user_id)
        return user

    def list_users(self) -> list[User]:
        return sorted(
            self.users.values(),
            key=lambda user: user.created_time,
        )


_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
