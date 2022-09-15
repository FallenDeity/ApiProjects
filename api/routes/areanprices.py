from api.utils import Price
from typing import TYPE_CHECKING
from fastapi import APIRouter, HTTPException, FastAPI

if TYPE_CHECKING:
    from api.setup import Database, Logs


class AreanPrices:

    __slots__: tuple[str, ...] = (
        "database",
        "logger",
    )
    router: APIRouter = APIRouter()

    def __init__(self, database: "Database", logger: "Logs") -> None:
        self.database = database
        self.logger = logger

    @staticmethod
    def intersection(items: list[list[Price]]) -> list[Price]:
        return list(set.intersection(*map(set, items)))

    async def get_by_id(self, _id: int) -> Price:
        result: Price = await self.database.prices.get_by_id(_id)
        if not result:
            self.logger.log(f"No commodity found with that id: {_id}", "error")
            raise HTTPException(status_code=404, detail="No commodity found with that ID")
        self.logger.log(f"Found commodity with id: {_id}", "info")
        return result

    async def get_by_state(self, state: str) -> list[Price]:
        result = await self.database.prices.get_by_state(state)
        if not result:
            self.logger.log(f"No commodity found with that state: {state}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"No commodity found with that state. Please check the spelling. Valid states are {', '.join(await self.database.prices.get_all_states)}",
            )
        self.logger.log(f"Found {len(result)} commodities with state: {state}", "info")
        return result

    async def get_by_district(self, district: str) -> list[Price]:
        result = await self.database.prices.get_by_district(district)
        if not result:
            self.logger.log(f"No commodity found with that district: {district}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"No commodity found with that district. Please check the spelling. Valid districts are {', '.join(await self.database.prices.get_all_districts)}",
            )
        self.logger.log(f"Found {len(result)} commodities with district: {district}", "info")
        return result

    async def get_by_market(self, market: str) -> list[Price]:
        result = await self.database.prices.get_by_market(market)
        if not result:
            self.logger.log(f"No commodity found with that market: {market}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"No commodity found with that market. Please check the spelling. Valid markets are {', '.join(await self.database.prices.get_all_markets)}",
            )
        self.logger.log(f"Found {len(result)} commodities with market: {market}", "info")
        return result

    async def get_by_commodity(self, commodity: str) -> list[Price]:
        result = await self.database.prices.get_by_commodity(commodity)
        if not result:
            self.logger.log(f"No commodity found with that name: {commodity}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"No commodity found with that name. Please check the spelling. Valid commodities are {', '.join(await self.database.prices.get_all_commodities)}",
            )
        self.logger.log(f"Found {len(result)} commodities with name: {commodity}", "info")
        return result

    async def get_by_budget(self, initial: int, final: int) -> list[Price]:
        result = await self.database.prices.get_between_budget(initial, final)
        if not result:
            self.logger.log(f"No commodity found with that budget: {initial} - {final}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"No commodity found with that budget. Please check the spelling. Valid budgets are {', '.join(await self.database.prices.get_all_budgets)}",
            )
        self.logger.log(f"Found {len(result)} commodities with budget: {initial} - {final}", "info")
        return result

    async def get_items(
        self,
        _id: int | None = None,
        state: str | None = None,
        district: str | None = None,
        market: str | None = None,
        commodity: str | None = None,
        initial: int | None = None,
        final: int | None = None,
    ) -> list[Price]:
        holder = []
        if _id:
            holder.append([await self.get_by_id(_id)])
        if state:
            holder.append(await self.get_by_state(state))
        if district:
            holder.append(await self.get_by_district(district))
        if market:
            holder.append(await self.get_by_market(market))
        if commodity:
            holder.append(await self.get_by_commodity(commodity))
        if initial and final:
            holder.append(await self.get_by_budget(initial, final))
        return self.intersection(holder)

    def setup(self) -> None:
        self.router.add_api_route("/prices/id", self.get_by_id, methods=["GET"], response_model=Price)
        self.router.add_api_route("/prices/state", self.get_by_state, methods=["GET"], response_model=list[Price])
        self.router.add_api_route(
            "/prices/district", self.get_by_district, methods=["GET"], response_model=list[Price]
        )
        self.router.add_api_route("/prices/market", self.get_by_market, methods=["GET"], response_model=list[Price])
        self.router.add_api_route(
            "/prices/commodity", self.get_by_commodity, methods=["GET"], response_model=list[Price]
        )
        self.router.add_api_route(
            "/prices/budget", self.get_by_budget, methods=["GET"], response_model=list[Price]
        )
        self.router.add_api_route("/prices/filter", self.get_items, methods=["GET"], response_model=list[Price])


async def setup(app: FastAPI, database: "Database", logger: "Logs") -> None:
    areanprices = AreanPrices(database, logger)
    areanprices.setup()
    app.include_router(areanprices.router)
    logger.log("AreanPrices routes loaded", "info")
