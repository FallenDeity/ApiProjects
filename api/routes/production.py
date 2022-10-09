from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI, HTTPException

from api.utils import Production

if TYPE_CHECKING:
    from api.setup import Database, Logs


class Produce:

    __slots__: tuple[str, ...] = (
        "database",
        "logger",
    )
    router: APIRouter = APIRouter()

    def __init__(self, database: "Database", logger: "Logs") -> None:
        self.database = database
        self.logger = logger

    @staticmethod
    def intersection(items: list[list[Production]]) -> list[Production]:
        res = set.intersection(*map(lambda x: set([i.ID for i in x]), items))
        return [i for i in sum(items, []) if i.ID in res]

    async def get_by_crop(self, crop: str) -> list[Production]:
        result = await self.database.production.get_by_name(crop)
        if not result:
            self.logger.log(f"No production data found with that crop: {crop}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"No production data found with that crop. Please check the spelling. Valid crops are {', '.join(await self.database.production.get_all_crops)}",
            )
        self.logger.log(f"Found {len(result)} production data with crop: {crop}", "info")
        return result

    async def get_by_frequency(self, frequency: str) -> list[Production]:
        result = await self.database.production.get_by_frequency(frequency)
        if not result:
            self.logger.log(f"No production data found with that frequency: {frequency}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"No production data found with that frequency. Please check the spelling. Valid frequencies are {', '.join(await self.database.production.get_all_seasons)}",
            )
        self.logger.log(f"Found {len(result)} production data with frequency: {frequency}", "info")
        return result

    async def get_avg_production(self, average: float) -> list[Production]:
        result = await self.database.production.get_by_avg_production(average)
        if not result:
            self.logger.log(f"No production data found with that average: {average}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"No production data found with that average.",
            )
        self.logger.log(f"Found {len(result)} production data with average: {average}", "info")
        return result

    async def get_produce(
        self, crop: str | None = None, frequency: str | None = None, average: float | None = None
    ) -> list[Production]:
        holder = []
        if crop:
            holder.append(await self.get_by_crop(crop))
        if frequency:
            holder.append(await self.get_by_frequency(frequency))
        if average:
            holder.append(await self.get_avg_production(average))
        return self.intersection(holder)

    def setup(self) -> None:
        self.router.add_api_route("/produce/crop", self.get_by_crop, methods=["GET"], response_model=list[Production])
        self.router.add_api_route("/produce/frequency", self.get_by_frequency, methods=["GET"], response_model=list[Production])
        self.router.add_api_route("/produce/average", self.get_avg_production, methods=["GET"], response_model=list[Production])
        self.router.add_api_route("/produce/filter", self.get_produce, methods=["GET"], response_model=list[Production])


async def setup(app: FastAPI, database: "Database", logger: "Logs") -> None:
    production = Produce(database, logger)
    production.setup()
    app.include_router(production.router, prefix="/api/v1", tags=["Production"])
    logger.log("Production routes setup complete", "info")
