import base64
import os
from typing import TYPE_CHECKING

from fastapi import APIRouter, FastAPI, UploadFile
from fastapi.responses import ORJSONResponse

if TYPE_CHECKING:
    from api.setup import Database, Logs


class Identifier:
    __slots__: tuple[str, ...] = ("database", "logger")
    router: APIRouter = APIRouter()
    ENDPOINT_INFO: str = "https://api.plant.id/v2/identify"
    ENPOINT_DIAGNOSE: str = "https://api.plant.id/v2/health_assessment"
    API_TOKEN: str = os.getenv("PLANT_ID")
    HEADERS: dict[str, str] = {"Content-Type": "application/json", "Api-Key": API_TOKEN}
    INFO_DETAILS: list[str] = [
        "common_names",
        "edible_parts",
        "gbif_id",
        "name_authority",
        "propagation_methods",
        "synonyms",
        "taxonomy",
        "url",
        "wiki_description",
        "wiki_image",
    ]
    DIAGNOSE_DETAILS: list[str] = [
        "cause",
        "common_names",
        "classification",
        "description",
        "treatment",
        "url",
    ]

    def __init__(self, database: "Database", logger: "Logs") -> None:
        self.database = database
        self.logger = logger

    @staticmethod
    async def encode_image(file: UploadFile) -> str:
        return base64.b64encode(await file.read()).decode("ascii")

    async def identify(self, file: UploadFile) -> ORJSONResponse:
        response = await self.database.client.post(
            self.ENDPOINT_INFO,
            headers=self.HEADERS,
            json={"images": [await self.encode_image(file)], "plant_details": self.INFO_DETAILS},
        )
        return ORJSONResponse(await response.json())

    async def diagnose(self, file: UploadFile) -> ORJSONResponse:
        response = await self.database.client.post(
            self.ENPOINT_DIAGNOSE,
            headers=self.HEADERS,
            json={"images": [await self.encode_image(file)], "plant_details": self.DIAGNOSE_DETAILS},
        )
        return ORJSONResponse(await response.json())

    def setup(self) -> None:
        self.router.add_api_route("/upload/identify", self.identify, methods=["POST"], response_class=ORJSONResponse)
        self.router.add_api_route("/upload/diagnose", self.diagnose, methods=["POST"], response_class=ORJSONResponse)


async def setup(app: FastAPI, database: "Database", logger: "Logs") -> None:
    identifier = Identifier(database, logger)
    identifier.setup()
    app.include_router(identifier.router, prefix="/api/v1", tags=["identifier"])
    logger.log("Identifier routes loaded", "info")
