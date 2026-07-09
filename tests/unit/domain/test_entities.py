from agentsphere.domain.entities.tenant import TenantEntity
from agentsphere.domain.entities.user import UserEntity
from agentsphere.domain.entities.api_key import ApiKeyEntity


class TestTenantEntity:
    def test_create_tenant(self):
        tenant = TenantEntity(name="Test", slug="test")
        assert tenant.name == "Test"
        assert tenant.slug == "test"
        assert tenant.is_active is True


class TestUserEntity:
    def test_create_user(self):
        user = UserEntity(email="test@example.com", role="admin")
        assert user.email == "test@example.com"
        assert user.role == "admin"


class TestApiKeyEntity:
    def test_create_api_key(self):
        key = ApiKeyEntity(name="Test Key")
        assert key.name == "Test Key"
        assert key.is_active is True
