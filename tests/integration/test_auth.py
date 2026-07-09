import pytest


class TestAuthEndpoints:
    @pytest.mark.needs_db
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, client):
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "nonexistent@test.com", "password": "wrong"},
        )
        assert response.status_code in (401, 422)

    @pytest.mark.asyncio
    async def test_refresh_without_token(self, client):
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": ""},
        )
        assert response.status_code in (401, 422)
