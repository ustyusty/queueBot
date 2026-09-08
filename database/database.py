import asyncio
from contextlib import asynccontextmanager
from typing import Any
from asyncpg import Record, Connection, create_pool, Pool, PostgresError
from collections.abc import AsyncGenerator
from .transaction import Transaction
from .exceptions import DatabaseConnectionError, DatabaseQueryError


class DataBase:
    def __init__(self,
                dsn: Any | None = None,
                min_size: int = 10,
                max_size: int = 10,
                max_queries: int = 50000,
                command_timeout: int = None,
                **pool_options: Any,
                ):

        if min_size < 0:
            raise ValueError("min_size must be non-negative")

        if max_size < 1:
            raise ValueError("max_size must be positive")

        if min_size > max_size:
            raise ValueError("min_size cannot be greater than max_size")

        if max_queries<1:
            raise ValueError("max_queries must be positive")
        
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._max_queries = max_queries
        self._pool_options = pool_options
        self._command_timeout = command_timeout

        self._pool: Pool | None = None

    def _require_pool(self) -> Pool:
        if self._pool is None:
            raise RuntimeError("Database pool is not initialized")
        return self._pool


    async def connect(self) -> None:
        if self._pool is not None:
            return
        try:
            pool = await create_pool(
                dsn = self._dsn,
                min_size = self._min_size,
                max_size = self._max_size,
                max_queries = self._max_queries,
                command_timeout = self._command_timeout,
                **self._pool_options,
            )
            
        except (OSError, PostgresError) as error:
            raise DatabaseConnectionError(
                "Failed to connect to PostgreSQL"
            ) from error
        else:
            self._pool = pool

    async def fetchall(self, query: str, *args: Any) -> list[Record]:
        pool = self._require_pool()
        try:
            async with pool.acquire() as conn:
                return await conn.fetch(query, *args)
    
        except PostgresError as error:
            raise DatabaseQueryError(
                "Database fetchall operation failed"
            ) from error
    
    async def fetchval(self, query: str, *args: Any) -> Any:
        pool = self._require_pool()
        try:
            async with pool.acquire() as conn:
                return await conn.fetchval(query, *args)
    
        except PostgresError as error:
            raise DatabaseQueryError(
                "Database fetchval operation failed"
            ) from error
        
    async def fetchrow(
        self,
        query: str,
        *args: Any,
    ) -> Record | None:
        pool = self._require_pool()
        try:
            async with pool.acquire() as conn:
                return await conn.fetchrow(query, *args)
    
        except PostgresError as error:
            raise DatabaseQueryError(
                "Database fetchrow operation failed"
            ) from error
        
    async def execute(self, query: str, *args: Any) -> str:
        pool = self._require_pool()
        try: 
            async with pool.acquire() as conn:
                return await conn.execute(query, *args)
            
        except PostgresError as error:
            raise DatabaseQueryError(
                "Database execute operation failed"
            ) from error

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[Transaction, None]:
        pool = self._require_pool()
        async with pool.acquire() as connection:
            async with connection.transaction():
                yield Transaction(connection)

    @asynccontextmanager
    async def listen(self, channel: str) -> AsyncGenerator[asyncio.Queue[str], None]:
        """Keep a dedicated PostgreSQL LISTEN connection for a caller.

        The queue is only a wake-up hint. Consumers must always replay the
        durable journal by cursor after receiving a notification.
        """
        if not channel.replace("_", "").isalnum():
            raise ValueError("Invalid PostgreSQL notification channel")
        pool = self._require_pool()
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=100)
        async with pool.acquire() as connection:
            def on_notification(_connection, _pid, _channel, payload):
                try:
                    queue.put_nowait(payload)
                except asyncio.QueueFull:
                    # A notification is only a hint; the next journal replay
                    # returns every missed event.
                    pass

            await connection.add_listener(channel, on_notification)
            try:
                yield queue
            finally:
                await connection.remove_listener(channel, on_notification)
        
    async def close(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None
        else:
            pass