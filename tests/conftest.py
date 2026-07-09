import asyncio
from uuid import UUID

import pytest
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient

from agentsphere.common.uuid7 import uuid7
from agentsphere.interfaces.api.app import create_app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def app():
    application = create_app()
    async with LifespanManager(application):
        yield application


@pytest.fixture
async def client(app):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def sample_tenant_id() -> UUID:
    return uuid7()


@pytest.fixture
def sample_user_id() -> UUID:
    return uuid7()
