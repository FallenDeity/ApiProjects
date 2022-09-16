import asyncio
import os

import asyncpg
import pandas as pd

from .models import Price, Production, Sql, User
from .postgres import DatabaseModel

__all__: tuple[str, ...] = (
    "AreaToPrices",
    "Database",
)


class Database:

    __slots__: tuple[str, ...] = ("prices", "pool", "LINK", "users", "production")
    pool: asyncpg.pool.Pool
    LINK: str

    def __init__(self) -> None:
        self.prices = AreaToPrices()
        self.users = Register()
        self.production = Produce()
        self.LINK = os.environ.get("DATABASE_URL")

    async def setup(self) -> None:
        self.pool = await asyncpg.create_pool(
            host=os.environ.get("DATABASE_HOST"),
            port=os.environ.get("DATABASE_PORT"),
            user=os.environ.get("DATABASE_USER"),
            password=os.environ.get("DATABASE_PASSWORD"),
            database=os.environ.get("DATABASE_NAME"),
            loop=asyncio.get_event_loop(),
        )
        await self.prices.setup(self)
        await self.users.setup(self)
        await self.production.setup(self)

    async def close(self) -> None:
        await self.pool.close()


class Produce(DatabaseModel):
    __slots__: tuple[str, ...] = ("database_pool", "LINES")
    path: str = "api/assets/yearly_production.csv"
    LINES: Sql
    TABLE: str = "production"
    BASE: str = "Agricultural Production Foodgrains "

    def read_data(self) -> pd.DataFrame:
        df = pd.read_csv(self.path)
        return df.fillna(0).values.tolist()

    async def setup(self, database: "Database") -> None:
        self.database_pool = database.pool
        await self.execute_statements()
        await self.exec_write_query(self.LINES.create)
        check = await self.exec_fetchone("SELECT * FROM production")
        if not check:
            data = self.read_data()
            agg = [data[i][:3] + [data[i][3:]] for i in range(len(data))]
            await self.exec_write_many(self.LINES.insert, (agg,))
            print("Production data loaded")

    @property
    async def get_all(self) -> list[Production]:
        data = await self.exec_fetchall("SELECT * FROM production")
        return [Production(*row) for row in data]

    @property
    async def get_all_crops(self) -> list[str]:
        data = await self.get_all
        return [i.CROP.replace(self.BASE, "").strip().split()[0] for i in data]

    @property
    async def get_all_seasons(self) -> list[str]:
        return ["Kharif", "Rabi"]

    async def get_by_id(self, _id: int) -> Production:
        data = await self.exec_fetchone("SELECT * FROM production WHERE ID = $1", (_id,))
        return Production(*data)

    async def get_by_name(self, name: str) -> list[Production]:
        data = await self.exec_fetchall("SELECT * FROM production WHERE CROP LIKE $1", (f"%{name}%",))
        return [Production(*i) for i in data]

    async def get_by_frequency(self, frequency: str) -> list[Production]:
        data = await self.exec_fetchall("SELECT * FROM production WHERE CROP LIKE $1", (f"%{frequency}",))
        return [Production(*row) for row in data]

    async def get_by_avg_production(self, avg_production: float) -> list[Production]:
        data = await self.exec_fetchall("SELECT * FROM prices WHERE SUM(VALUES) > $1", (avg_production,))
        return [Production(*row) for row in data]


class AreaToPrices(DatabaseModel):

    __slots__: tuple[str, ...] = ("database_pool", "LINES")
    PATH: str = "api/assets/area_and_prices.csv"
    TABLE: str = "prices"
    LINES: Sql

    def read_data(self, index: int) -> pd.DataFrame:
        df = pd.read_csv(self.PATH, index_col=index)
        return df

    async def setup(self, database: "Database") -> None:
        self.database_pool = database.pool
        await self.execute_statements()
        await self.exec_write_query(self.LINES.create)
        check = await self.exec_fetchone("SELECT * FROM prices")
        if not check:
            data = self.read_data(-1)
            await self.exec_write_many(self.LINES.insert, (data.values.tolist(),))
            print("Database has been setup successfully!")

    @property
    async def last_index(self) -> int:
        data = await self.exec_fetchone("SELECT MAX(ID) FROM prices")
        return int(data[0]) if data else 0

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

    async def get_districts_by_state(self, state: str) -> list[str]:
        data = await self.exec_fetchall("SELECT DISTINCT DISTRICT FROM prices WHERE STATE = $1", (state,))
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


class Register(DatabaseModel):

    __slots__: tuple[str, ...] = ("database_pool", "LINES")
    TABLE: str = "register"
    LINES: Sql

    async def setup(self, database: "Database") -> None:
        self.database_pool = database.pool
        await self.execute_statements()
        await self.exec_write_query(self.LINES.create)

    async def check_number(self, number: int) -> bool:
        data = await self.exec_fetchone("SELECT * FROM users WHERE PHONENUMBER = $1", (number,))
        return True if data else False

    async def login_user(self, number: int, password: str) -> bool:
        data = await self.exec_fetchone("SELECT * FROM users WHERE PHONENUMBER = $1 AND PASSWORD = $2", (number, password))
        return True if data else False

    async def register_user(self, user: User) -> bool:
        if await self.check_number(user.phone):
            return False
        await self.exec_write_query(self.LINES.insert, (*list(user.__dict__.values()),))
        return True

    async def update_password(self, number: int, password: str) -> None:
        await self.exec_write_query("UPDATE users SET PASSWORD = $1 WHERE PHONENUMBER = $2", (password, number))

    async def update_state(self, number: int, state: str) -> None:
        await self.exec_write_query("UPDATE users SET STATE = $1 WHERE PHONENUMBER = $2", (state, number))

    async def update_district(self, number: int, district: str) -> None:
        await self.exec_write_query("UPDATE users SET DISTRICT = $1 WHERE PHONENUMBER = $2", (district, number))

    async def get_user(self, number: int) -> User:
        data = await self.exec_fetchone("SELECT * FROM users WHERE PHONENUMBER = $1", (number,))
        return User(*data) if data else None

    async def delete_user(self, number: int) -> None:
        await self.exec_write_query("DELETE FROM users WHERE PHONENUMBER = $1", (number,))

    @property
    async def get_all_users(self) -> list[User]:
        data = await self.exec_fetchall("SELECT * FROM users")
        return [User(*row) for row in data]

    @property
    async def total_users(self) -> int:
        data = await self.exec_fetchone("SELECT COUNT(*) FROM users")
        return int(data[0]) if data else 0
