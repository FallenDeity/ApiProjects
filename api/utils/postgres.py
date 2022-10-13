import typing
from pathlib import Path

import aiofiles
import asyncpg

from .models import Sql

__all__: tuple[str, ...] = ("DatabaseModel",)


class DatabaseModel:

    __slots__: tuple[str, ...] = ("database_pool", "LINES")
    database_pool: asyncpg.pool.Pool
    TABLES: Path = Path(__file__).parent.parent / "bin" / "tables"
    TABLE: str
    LINES: Sql

    async def execute_statements(self) -> None:
        async with aiofiles.open(self.TABLES / f"{self.TABLE}.sql", "r") as file:
            scripts = await file.read()
        self.LINES = Sql(*[i for i in scripts.split(";") if i.strip()])

    async def exec_write_query(self, query: str, data: typing.Optional[tuple] = None) -> None:
        if data:
            await self.database_pool.execute(query, *data)
            return

        await self.database_pool.execute(query)

    async def exec_write_many(self, query: str, data: tuple[typing.Any, ...]) -> None:
        await self.database_pool.executemany(query, *data)

    async def exec_fetchone(self, query: str, data: typing.Optional[tuple] = None) -> typing.Optional[asyncpg.Record]:
        result: typing.Optional[asyncpg.Record] = await self.database_pool.fetchrow(query, *(data or []))
        return result

    async def exec_fetchall(
        self, query: str, data: typing.Optional[tuple[typing.Any, ...]] = None
    ) -> list[asyncpg.Record]:
        args: typing.Union[tuple, list] = data or []
        results: list[asyncpg.Record] = await self.database_pool.fetch(query, *args)
        return results
