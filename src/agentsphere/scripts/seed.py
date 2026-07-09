import structlog

from agentsphere.common.uuid7 import uuid7
from agentsphere.infrastructure.auth.password_hasher import PasswordHasher
from agentsphere.infrastructure.persistence.repositories.tenant_repository import TenantRepository
from agentsphere.infrastructure.persistence.repositories.user_repository import UserRepository
from agentsphere.interfaces.container import init_container

logger = structlog.get_logger(__name__)


async def seed() -> None:
    container = init_container()
    settings = container.core.settings()

    await container.core.db().init(
        settings.DATABASE_URL,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_MAX_OVERFLOW,
    )

    async with await container.core.db().get_session() as session:
        tenant_repo = TenantRepository(session=session)
        existing = await tenant_repo.get_by_slug("demo")
        if existing:
            logger.info("seed_skipped", reason="demo tenant already exists")
            return

        tenant_id = uuid7()
        await tenant_repo.create(
            id=tenant_id,
            name="Demo Tenant",
            slug="demo",
        )

        hasher = PasswordHasher()
        admin_password = settings.SEED_ADMIN_PASSWORD or "admin123"
        password_hash = hasher.hash(admin_password)

        user_repo = UserRepository(session=session)
        await user_repo.create(
            id=uuid7(),
            tenant_id=tenant_id,
            email=settings.SEED_ADMIN_EMAIL,
            password_hash=password_hash,
            display_name="Admin User",
            role="superadmin",
        )

        await session.commit()
        logger.info("seed_complete", tenant_id=str(tenant_id), email=settings.SEED_ADMIN_EMAIL)
