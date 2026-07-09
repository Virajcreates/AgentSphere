from unittest.mock import AsyncMock, MagicMock

import pytest

from agentsphere.application.use_cases.auth.create_api_key import CreateApiKeyUseCase
from agentsphere.common.exceptions import ValidationError
from agentsphere.common.uuid7 import uuid7


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeApiKeyRepo:
    def __init__(self, session=None):
        self._session = session
        self._created = None

    async def create(self, **kwargs):
        self._created = kwargs
        return kwargs

    async def get(self, id, tenant_id):
        return None


class FakeApiKeyHandler:
    def generate(self, tenant_id, key_id):
        return ("raw_key_value", "as_live_testprefix", "hashed_value")


class TestCreateApiKeyUseCase:
    @pytest.fixture
    def use_case(self):
        return CreateApiKeyUseCase(
            db=MagicMock(),
            api_key_repo_factory=FakeApiKeyRepo,
            api_key_handler=FakeApiKeyHandler(),
        )

    async def test_create_api_key(self, use_case):
        session = FakeSession()
        use_case._db.get_session = AsyncMock(return_value=session)

        result = await use_case.execute(
            tenant_id=uuid7(),
            name="Test Key",
            scopes=["conversations:read"],
        )
        assert result["name"] == "Test Key"
        assert result["key"] == "raw_key_value"
        assert "id" in result

    async def test_empty_name_raises_error(self, use_case):
        with pytest.raises(ValidationError):
            await use_case.execute(tenant_id=uuid7(), name="")