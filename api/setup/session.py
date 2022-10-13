import datetime
import pathlib
import typing

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from api.utils import Database

from .logger import Logs


class API:

    __slots__: tuple[str, ...] = (
        "database",
        "logger",
    )
    PATH: pathlib.Path = pathlib.Path(__file__).parent / "routes"
    app: FastAPI = FastAPI()
    database: Database
    uptime: datetime.datetime = datetime.datetime.now()
    templates: Jinja2Templates = Jinja2Templates(directory="api/assets/templates")

    def __init__(self) -> None:
        load_dotenv()
        self.database = Database()
        self.logger = Logs()
        self.prepare()

    async def _load_routes(self) -> None:
        for route in self.PATH.glob("*.py"):
            if route.name.startswith("_"):
                continue
            module = __import__(f"{self.PATH.name}.{route.stem}", fromlist=["setup"])
            await module.setup(self.app)
            self.logger.log(f"Loading {module}", "info")

    async def root(self, request: Request) -> typing.Any:
        return self.templates.TemplateResponse(
            "index.html",
            {"request": request, "name": __import__("api").__name__, "version": __import__("api").__version__},
        )

    def prepare(self) -> None:
        self.app.add_event_handler("startup", self.database.setup)
        self.app.add_event_handler("startup", self._load_routes)
        self.app.add_event_handler("shutdown", self.database.close)
        self.app.add_api_route("/", self.root, response_class=HTMLResponse)
        self.logger.log("API started", "info")

    @property
    def get_app(self) -> FastAPI:
        return self.app

    @property
    def up(self) -> datetime.datetime:
        return self.uptime

    def run(self, *_args: typing.Optional[typing.Any], **_kwargs: typing.Optional[typing.Any]) -> None:
        uvicorn.run(self.app, debug=True)
