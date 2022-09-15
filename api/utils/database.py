import asyncpg
import os
import pandas as pd
from api.bin import SQL
from .models import Price
from .postgres import DatabaseModel


__all__: tuple[str, ...] = (
    "AreaToPrices",
    "Database",
)


class Database:

    __slots__: tuple[str, ...] = ("prices", "pool", "LINK")
    pool: asyncpg.pool.Pool
    LINK: str

    def __init__(self) -> None:
        self.prices = AreaToPrices()
        self.LINK = os.environ.get("DATABASE")

    async def setup(self) -> None:
        self.pool = await asyncpg.create_pool(self.LINK)
        await self.prices.setup(self)

    async def close(self) -> None:
        await self.pool.close()


class AreaToPrices(DatabaseModel):

    __slots__: tuple[str, ...] = ("database_pool",)
    PATH: str = "api/assets/area_and_prices.csv"

    def read_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.PATH, index_col=-1)
        return df

    async def setup(self, database: "Database") -> None:
        self.database_pool = database.pool
        await self.exec_write_query(SQL.area_to_prices_c)
        check = await self.exec_fetchone("SELECT * FROM prices")
        if not check:
            data = self.read_data()
            await self.exec_write_many(SQL.area_to_prices_i, (data.values.tolist(),))

    @property
    async def last_index(self) -> int:
        data = await self.exec_fetchone("SELECT MAX(ID) FROM prices")
        return data[0] if data else 0

    @property
    async def get_all_states(self) -> list[str]:
        data = await self.exec_fetchall("SELECT DISTINCT STATE FROM prices")
        return [row[0] for row in data]

    @property
    async def get_all_commodities(self) -> list[str]:
        data = await self.exec_fetchall("SELECT DISTINCT COMMODITY FROM prices")
        return [row[0] for row in data]

    @property
    async def get_all_districts(self) -> list[str]:
        data = await self.exec_fetchall("SELECT DISTINCT DISTRICT FROM prices")
        return [row[0] for row in data]

    @property
    async def get_all_markets(self) -> list[str]:
        data = await self.exec_fetchall("SELECT DISTINCT MARKET FROM prices")
        return [row[0] for row in data]

    async def get_by_id(self, _id: int) -> Price:
        data = await self.exec_fetchone("SELECT * FROM prices WHERE ID = $1", (_id,))
        return Price(*data) if data else None

    async def get_by_state(self, state: str) -> list[Price]:
        data = await self.exec_fetchall("SELECT * FROM prices WHERE STATE = $1", (state,))
        return [Price(*row) for row in data]

    async def get_by_district(self, district: str) -> list[Price]:
        data = await self.exec_fetchall("SELECT * FROM prices WHERE DISTRICT = $1", (district,))
        return [Price(*row) for row in data]

    async def get_by_market(self, market: str) -> list[Price]:
        data = await self.exec_fetchall("SELECT * FROM prices WHERE MARKET = $1", (market,))
        return [Price(*row) for row in data]

    async def get_by_commodity(self, commodity: str) -> list[Price]:
        data = await self.exec_fetchall("SELECT * FROM prices WHERE COMMODITY = $1", (commodity,))
        return [Price(*row) for row in data]

    async def get_between_budget(self, min_price: int, max_price: int) -> list[Price]:
        if max_price < min_price:
            min_price, max_price = max_price, min_price
        data = await self.exec_fetchall("SELECT * FROM prices WHERE MODAL_PRICE BETWEEN $1 AND $2", (min_price, max_price))
        return [Price(*row) for row in data]
