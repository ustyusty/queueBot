from collections.abc import Iterable, Sequence
from typing import Any
from asyncpg import Record, Connection

import logging
logger = logging.getLogger(__name__)

class Transaction:
    def __init__(self, connection: Connection):
        self._connection = connection

    async def execute(self, query: str, *args: Any) -> str:
        return await self._connection.execute(query, *args)

    async def executemany(
        self,
        query: str,
        args: Iterable[Sequence[Any]],
    ) -> None:
        await self._connection.executemany(query, args)

    async def fetchrow(self, query: str, *args: Any) -> Record | None:
        return await self._connection.fetchrow(query, *args)

    async def fetchval(self, query: str, *args: Any) -> Any:
        return await self._connection.fetchval(query, *args)
    
    async def fetchall(self, query: str, *args: Any) -> list[Record]:
        return await self._connection.fetch(query, *args)