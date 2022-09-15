import os
import uvicorn
from .logger import Logs
from api.utils import Database
from fastapi import FastAPI


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

    async def _load_routes(self) -> None:
        for file in os.listdir(self.PATH):
            if file.endswith(".py") and not file.startswith("_"):
                module = __import__(f"{'.'.join(self.PATH.split('/'))}.{file[:-3]}", fromlist=["setup"])
                await module.setup(self.app, self.database, self.logger)

    def run(self) -> None:
        self.app.add_event_handler("startup", self.database.setup)
        self.app.add_event_handler("startup", self._load_routes)
        self.app.add_event_handler("shutdown", self.database.close)
        self.logger.log("API started", "info")
        uvicorn.run(self.app, debug=True)
