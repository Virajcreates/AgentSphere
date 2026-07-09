from agentsphere.config.database import DatabaseManager


async def check_migration_state(db: DatabaseManager) -> tuple[bool, str]:
    try:
        async with await db.get_session() as session:
            result = await session.execute(
                __import__("sqlalchemy").text("SELECT version_num FROM alembic_version")
            )
            row = result.scalar_one_or_none()
            if row is None:
                return False, "No migrations have been applied"
            head_version = row
            return True, f"Migrations at version {head_version}"
    except Exception as exc:
        return False, f"Could not check migration state: {exc}"
