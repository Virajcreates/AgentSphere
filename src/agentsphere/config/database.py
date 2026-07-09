from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class DatabaseManager:
    _engine: AsyncEngine | None = None
    _session_factory: async_sessionmaker[AsyncSession] | None = None

    async def init(self, database_url: str, pool_size: int = 10, max_overflow: int = 20) -> None:
        self._engine = create_async_engine(
            database_url,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=False,
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

    async def close(self) -> None:
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            raise RuntimeError("Database not initialized")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            raise RuntimeError("Database not initialized")
        return self._session_factory

    async def get_session(self) -> AsyncSession:
        return self.session_factory()

    async def health_check(self) -> bool:
        try:
            async with await self.get_session() as session:
                await session.execute(
                    __import__("sqlalchemy").text("SELECT 1")
                )
            return True
        except Exception:
            return False
