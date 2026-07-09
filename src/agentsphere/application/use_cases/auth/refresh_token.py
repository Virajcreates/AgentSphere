from typing import Any

from agentsphere.common.exceptions import UnauthorizedError


class RefreshTokenUseCase:
    def __init__(self, jwt_handler: Any) -> None:
        self._jwt_handler = jwt_handler

    async def execute(self, refresh_token: str) -> dict[str, Any]:
        payload = await self._jwt_handler.validate_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid refresh token")

        await self._jwt_handler.revoke_token(refresh_token)

        access_token = await self._jwt_handler.create_access_token(
            user_id=payload["sub"],
            tenant_id=payload["tenant_id"],
            role=payload.get("role", "viewer"),
        )
        new_refresh_token = await self._jwt_handler.create_refresh_token(
            user_id=payload["sub"],
            tenant_id=payload["tenant_id"],
        )

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
