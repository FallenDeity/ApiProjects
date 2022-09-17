import datetime
import os
from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI, HTTPException
from fastapi.responses import ORJSONResponse

if TYPE_CHECKING:
    from api.setup import Database, Logs


class Climate:

    __slots__: tuple[str, ...] = ("database", "logger")
    router: APIRouter = APIRouter()
    WEATHER_API: str = os.getenv("WEATHER_ID")
    ENDPOINT: str = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/"
    POINTS: list[str] = ["timeline", "history", "historysummary"]

    def __init__(self, database: "Database", logger: "Logs") -> None:
        self.database = database
        self.logger = logger

    async def forecast(self, phonenumber: int, location: str | None = None) -> ORJSONResponse:
        if location is None:
            user = await self.database.users.get_user(phonenumber)
            if not user:
                self.logger.log(f"No user found with that number: {phonenumber}", "error")
                raise HTTPException(status_code=404, detail="No user found with that username")
            location = f"{user.state}, {user.district}"
        response = await self.database.client.get(
            self.ENDPOINT + "weatherdata/forecast",
            params={
                "locations": location,
                "aggregateHours": "24",
                "forecastDays": "15",
                "alertLevel": "detail",
                "includeAstronomy": "true",
                "unitGroup": "metric",
                "contentType": "json",
                "key": self.WEATHER_API,
            },
        )
        return ORJSONResponse(await response.json())

    async def history(self, phonenumber: int, location: str | None = None) -> ORJSONResponse:
        if location is None:
            user = await self.database.users.get_user(phonenumber)
            if not user:
                self.logger.log(f"No user found with that number: {phonenumber}", "error")
                raise HTTPException(status_code=404, detail="No user found with that username")
            location = f"{user.state}, {user.district}"
        response = await self.database.client.get(
            self.ENDPOINT + "weatherdata/history",
            params={
                "key": self.WEATHER_API,
                "location": location,
                "aggregateHours": 24,
                "period": "lastyear",
                "extendedStats": "true",
                "unitGroup": "metric",
                "contentType": "json",
            },
        )
        return ORJSONResponse(await response.json())

    async def timeline(self, phonenumber: int, location: str | None = None) -> ORJSONResponse:
        if location is None:
            user = await self.database.users.get_user(phonenumber)
            if not user:
                self.logger.log(f"No user found with that number: {phonenumber}", "error")
                raise HTTPException(status_code=404, detail="No user found with that username")
            location = f"{user.state}, {user.district}"
        date = datetime.datetime.now().strftime("%Y-%m-%d")
        response = await self.database.client.get(
            self.ENDPOINT + f"timeline/{location}/{date}",
            params={"key": self.WEATHER_API, "include": "fcst,obs,stats,hours,alerts", "unitGroup": "metric"},
        )
        return ORJSONResponse(await response.json())

    def setup(self) -> None:
        self.router.add_api_route("/weather/forecast", self.forecast, methods=["GET"], response_class=ORJSONResponse)
        self.router.add_api_route("/weather/history", self.history, methods=["GET"], response_class=ORJSONResponse)
        self.router.add_api_route("/weather/timeline", self.timeline, methods=["GET"], response_class=ORJSONResponse)


async def setup(app: FastAPI, database: "Database", logger: "Logs") -> None:
    climate = Climate(database, logger)
    climate.setup()
    app.include_router(climate.router, prefix="/api/v1", tags=["weather"])
    logger.log("Weather API setup complete", "info")
