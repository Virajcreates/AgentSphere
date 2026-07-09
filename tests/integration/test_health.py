import pytest


class TestHealthEndpoints:
    @pytest.mark.asyncio
    async def test_health(self, client):
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    @pytest.mark.asyncio
    async def test_version(self, client):
        response = await client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "environment" in data

    @pytest.mark.asyncio
    async def test_ready(self, client):
        response = await client.get("/ready")
        assert response.status_code == 200
        data = response.json()
        assert "checks" in data

    @pytest.mark.asyncio
    async def test_healthz(self, client):
        response = await client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "checks" in data
