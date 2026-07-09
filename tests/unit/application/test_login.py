from unittest.mock import AsyncMock, MagicMock

import pytest

from agentsphere.application.use_cases.auth.login import LoginUseCase
from agentsphere.common.exceptions import UnauthorizedError
from agentsphere.common.uuid7 import uuid7


class FakeSession:
    def __init__(self):
        self._users = {}

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass

    def add_user(self, user: dict):
        self._users[user["email"]] = user


class FakeUserRepo:
    def __init__(self, session=None):
        self._session = session
        self._users = {}

    async def get_by_email(self, email: str) -> dict | None:
        return self._users.get(email)

    def add_user(self, user: dict):
        self._users[user["email"]] = user


class FakeJWT:
    async def create_access_token(self, user_id, tenant_id, role):
        return f"access_token_{user_id}"

    async def create_refresh_token(self, user_id, tenant_id):
        return f"refresh_token_{user_id}"


class FakePasswordHasher:
    def verify(self, password, password_hash):
        return password == password_hash


class TestLoginUseCase:
    @pytest.fixture
    def use_case(self):
        return LoginUseCase(
            db=MagicMock(),
            user_repo_factory=FakeUserRepo,
            jwt_handler=FakeJWT(),
            password_hasher=FakePasswordHasher(),
        )

    async def test_successful_login(self, use_case):
        session = FakeSession()
        session.add_user({
            "id": uuid7(),
            "tenant_id": uuid7(),
            "email": "test@example.com",
            "password_hash": "correct-password",
            "display_name": "Test",
            "role": "admin",
            "is_active": True,
        })
        use_case._db.get_session = AsyncMock(return_value=session)

        user_repo = FakeUserRepo()
        user_repo._users = session._users
        use_case._user_repo_factory = MagicMock(return_value=user_repo)

        result = await use_case.execute("test@example.com", "correct-password")
        assert "access_token" in result
        assert "refresh_token" in result

    async def test_invalid_password(self, use_case):
        session = FakeSession()
        session.add_user({
            "id": uuid7(),
            "tenant_id": uuid7(),
            "email": "test@example.com",
            "password_hash": "correct-password",
            "display_name": "Test",
            "role": "admin",
            "is_active": True,
        })
        use_case._db.get_session = AsyncMock(return_value=session)

        user_repo = FakeUserRepo()
        user_repo._users = session._users
        use_case._user_repo_factory = MagicMock(return_value=user_repo)

        with pytest.raises(UnauthorizedError):
            await use_case.execute("test@example.com", "wrong-password")

    async def test_invalid_email(self, use_case):
        session = FakeSession()
        use_case._db.get_session = AsyncMock(return_value=session)

        user_repo = FakeUserRepo()
        use_case._user_repo_factory = MagicMock(return_value=user_repo)

        with pytest.raises(UnauthorizedError):
            await use_case.execute("nonexistent@example.com", "password")