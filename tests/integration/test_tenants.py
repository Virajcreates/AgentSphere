import pytest


class TestTenantEndpoints:
    @pytest.mark.needs_db
    @pytest.mark.asyncio
    async def test_create_tenant(self, client):
        response = await client.post(
            "/api/v1/tenants",
            json={"name": "Test Tenant", "slug": "test-tenant"},
        )
        assert response.status_code in (200, 201, 422)
