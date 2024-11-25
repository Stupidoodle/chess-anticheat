from typing import Dict, Optional, List
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer
import jwt
from dataclasses import dataclass


@dataclass
class SecurityConfig:
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7


class SecurityManager:
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

    async def create_access_token(
        self, data: Dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta or timedelta(minutes=self.config.access_token_expire_minutes)
        )
        to_encode.update({"exp": expire})

        return jwt.encode(
            to_encode, self.config.secret_key, algorithm=self.config.algorithm
        )

    async def verify_token(self, token: str) -> Dict:
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token, self.config.secret_key, algorithms=[self.config.algorithm]
            )
            return payload
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=401, detail="Invalid authentication credentials"
            )


class RoleBasedAuth:
    def __init__(self, security_manager: SecurityManager):
        self.security_manager = security_manager

    def require_roles(self, required_roles: List[str]):
        """Role-based authorization decorator."""

        async def role_checker(
            token: str = Depends(self.security_manager.oauth2_scheme),
        ):
            payload = await self.security_manager.verify_token(token)
            user_roles = payload.get("roles", [])

            if not any(role in user_roles for role in required_roles):
                raise HTTPException(status_code=403, detail="Insufficient permissions")
            return payload

        return role_checker
