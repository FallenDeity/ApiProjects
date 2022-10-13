import datetime
import pathlib
import typing

import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from api.utils import Database

from .logger import Logs


class API:

    __slots__: tuple[str, ...] = (
        "database",
        "logger",
    )
    app: FastAPI = FastAPI()
    database: Database
    PATH: pathlib.Path = pathlib.Path(__file__).parent.parent / "routes"
    uptime: datetime.datetime = datetime.datetime.now()
    templates: Jinja2Templates = Jinja2Templates(directory="api/assets/templates")

    def __init__(self) -> None:
        self.database = Database()
        self.logger = Logs()
        self.prepare()

    def index(self, request: Request) -> typing.Any:
        return self.templates.TemplateResponse(
            "index.html",
            {"request": request, "name": __import__("api").__name__, "version": __import__("api").__version__},
        )

    async def _load_routes(self) -> None:
        for route in self.PATH.glob("*.py"):
            if route.name.startswith("_"):
                continue
            module = __import__(f"{self.PATH.parent.name}.{self.PATH.name}.{route.stem}", fromlist=["setup"])
            await module.setup(self.app, self.database, self.logger)

    def prepare(self) -> None:
        self.app.add_event_handler("startup", self.database.setup)
        self.app.add_event_handler("startup", self._load_routes)
        self.app.add_event_handler("shutdown", self.database.close)
        self.app.add_route("/", self.index)

    @property
    def get_app(self) -> FastAPI:
        return self.app

    @property
    def up(self) -> datetime.datetime:
        return self.uptime

    def run(self, *_args: typing.Optional[typing.Any], **_kwargs: typing.Optional[typing.Any]) -> None:
        uvicorn.run(self.app, debug=True)
