from unittest.mock import AsyncMock, MagicMock

import pytest

from agentsphere.application.use_cases.tenant.create_tenant import CreateTenantUseCase
from agentsphere.common.exceptions import ConflictError, ValidationError


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


class FakeTenantRepo:
    def __init__(self, session=None):
        self._session = session
        self._tenants = {}

    async def get_by_slug(self, slug: str) -> dict | None:
        return self._tenants.get(slug)

    async def create(self, **kwargs) -> dict:
        self._tenants[kwargs["slug"]] = kwargs
        return kwargs


class TestCreateTenantUseCase:
    @pytest.fixture
    def use_case(self):
        return CreateTenantUseCase(
            db=MagicMock(),
            tenant_repo_factory=FakeTenantRepo,
        )

    async def test_create_tenant(self, use_case):
        session = FakeSession()
        use_case._db.get_session = AsyncMock(return_value=session)

        result = await use_case.execute(name="Test Tenant", slug="test-tenant")
        assert result["name"] == "Test Tenant"
        assert result["slug"] == "test-tenant"

    async def test_duplicate_slug(self, use_case):
        session = FakeSession()
        use_case._db.get_session = AsyncMock(return_value=session)

        repo = FakeTenantRepo()
        await repo.create(id="existing", name="Existing", slug="duplicate")
        use_case._tenant_repo_factory = MagicMock(return_value=repo)

        with pytest.raises(ConflictError):
            await use_case.execute(name="Another", slug="duplicate")

    async def test_empty_name(self, use_case):
        with pytest.raises(ValidationError):
            await use_case.execute(name="", slug="test")

    async def test_empty_slug(self, use_case):
        with pytest.raises(ValidationError):
            await use_case.execute(name="Test", slug="")