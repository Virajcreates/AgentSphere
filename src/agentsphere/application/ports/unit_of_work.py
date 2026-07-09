from contextlib import AbstractAsyncContextManager
from typing import Protocol


class UnitOfWork(AbstractAsyncContextManager["UnitOfWork"], Protocol):
    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
