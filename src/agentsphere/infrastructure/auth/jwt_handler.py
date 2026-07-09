import datetime
from typing import Any
from uuid import UUID

import jwt

from agentsphere.config.settings import Settings


class JWTHandler:
    def __init__(self, settings: Settings):
        self._secret = settings.JWT_SECRET
        self._algorithm = settings.JWT_ALGORITHM
        self._access_expire = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self._refresh_expire = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    async def create_access_token(self, user_id: UUID, tenant_id: UUID, role: str) -> str:
        now = datetime.datetime.now(datetime.UTC)
        payload = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "role": role,
            "type": "access",
            "iat": now,
            "exp": now + datetime.timedelta(minutes=self._access_expire),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    async def create_refresh_token(self, user_id: UUID, tenant_id: UUID) -> str:
        now = datetime.datetime.now(datetime.UTC)
        payload = {
            "sub": str(user_id),
            "tenant_id": str(tenant_id),
            "type": "refresh",
            "iat": now,
            "exp": now + datetime.timedelta(days=self._refresh_expire),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    async def validate_token(self, token: str) -> dict[str, Any] | None:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return payload
        except jwt.PyJWTError:
            return None

    async def revoke_token(self, token: str) -> None:
        pass
