from collections.abc import Callable
from typing import Any

from agentsphere.application.ports.repositories import UserRepositoryProtocol
from agentsphere.common.exceptions import ForbiddenError, UnauthorizedError
from agentsphere.domain.value_objects.email import Email


class LoginUseCase:
    def __init__(
        self,
        db: Any,
        user_repo_factory: Callable[..., UserRepositoryProtocol],
        jwt_handler: Any,
        password_hasher: Any,
    ) -> None:
        self._db = db
        self._user_repo_factory = user_repo_factory
        self._jwt_handler = jwt_handler
        self._password_hasher = password_hasher

    async def execute(self, email: str, password: str) -> dict[str, Any]:
        async with await self._db.get_session() as session:
            user_repo = self._user_repo_factory(session=session)
            email_vo = Email(email)
            user = await user_repo.get_by_email(email_vo.value)
            if not user:
                raise UnauthorizedError("Invalid email or password")

            if not user.get("is_active", True):
                raise ForbiddenError("Account is deactivated")

            if not self._password_hasher.verify(password, user["password_hash"]):
                raise UnauthorizedError("Invalid email or password")

            access_token = await self._jwt_handler.create_access_token(
                user_id=user["id"],
                tenant_id=user["tenant_id"],
                role=user["role"],
            )
            refresh_token = await self._jwt_handler.create_refresh_token(
                user_id=user["id"],
                tenant_id=user["tenant_id"],
            )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
