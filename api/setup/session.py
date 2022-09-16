import os
import typing

import uvicorn
from fastapi import FastAPI

from api.utils import Database

from .logger import Logs


class API:

    __slots__: tuple[str, ...] = (
        "database",
        "logger",
    )
    PATH: str = "api/routes"
    app: FastAPI = FastAPI()
    database: Database

    def __init__(self) -> None:
        self.database = Database()
        self.logger = Logs()
        self.prepare()

    async def _load_routes(self) -> None:
        for file in os.listdir(self.PATH):
            if file.endswith(".py") and not file.startswith("_"):
                module = __import__(f"{'.'.join(self.PATH.split('/'))}.{file[:-3]}", fromlist=["setup"])
                await module.setup(self.app, self.database, self.logger)

    def prepare(self) -> None:
        self.app.add_event_handler("startup", self.database.setup)
        self.app.add_event_handler("startup", self._load_routes)
        self.app.add_event_handler("shutdown", self.database.close)
        self.logger.log("API started", "info")

    @property
    def get_app(self) -> FastAPI:
        return self.app

    def run(self, *_args: typing.Optional[typing.Any], **_kwargs: typing.Optional[typing.Any]) -> None:
        uvicorn.run(self.app, debug=True)
