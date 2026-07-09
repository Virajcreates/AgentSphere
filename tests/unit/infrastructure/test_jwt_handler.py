import pytest

from agentsphere.common.uuid7 import uuid7
from agentsphere.config.settings import Settings
from agentsphere.infrastructure.auth.jwt_handler import JWTHandler


@pytest.fixture
def jwt_handler():
    settings = Settings(JWT_SECRET="test-secret-that-is-long-enough-32chars")
    return JWTHandler(settings)


class TestJWTHandler:
    async def test_create_access_token(self, jwt_handler):
        user_id = uuid7()
        tenant_id = uuid7()
        token = await jwt_handler.create_access_token(user_id, tenant_id, "admin")
        assert isinstance(token, str)
        assert len(token) > 20

    async def test_validate_valid_token(self, jwt_handler):
        user_id = uuid7()
        tenant_id = uuid7()
        token = await jwt_handler.create_access_token(user_id, tenant_id, "admin")
        payload = await jwt_handler.validate_token(token)
        assert payload is not None
        assert payload["sub"] == str(user_id)
        assert payload["tenant_id"] == str(tenant_id)
        assert payload["role"] == "admin"
        assert payload["type"] == "access"

    async def test_validate_invalid_token(self, jwt_handler):
        payload = await jwt_handler.validate_token("invalid.token.here")
        assert payload is None

    async def test_create_refresh_token(self, jwt_handler):
        user_id = uuid7()
        tenant_id = uuid7()
        token = await jwt_handler.create_refresh_token(user_id, tenant_id)
        payload = await jwt_handler.validate_token(token)
        assert payload["type"] == "refresh"
