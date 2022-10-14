import datetime
import pathlib
import typing

import uvicorn
from fastapi import FastAPI, Request, HTTPException, Form
from fastapi.responses import HTMLResponse
from fastapi.routing import Mount
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api.utils import Database, User

from .logger import Logs


class API:

    __slots__: tuple[str, ...] = (
        "database",
        "logger",
        "farmers",
        "app",
    )
    farmers: list[User]
    app: FastAPI
    database: Database
    PATH: pathlib.Path = pathlib.Path(__file__).parent.parent / "routes"
    uptime: datetime.datetime = datetime.datetime.now()
    templates: Jinja2Templates = Jinja2Templates(directory="api/assets/templates")
    routes: list[Mount] = [
        Mount("/static", StaticFiles(directory="api/assets/templates/static"), name="static"),
        Mount("/images", StaticFiles(directory="api/assets/images"), name="images"),
    ]

    def __init__(self) -> None:
        self.app = FastAPI(routes=self.routes)
        self.database = Database()
        self.logger = Logs()
        self.prepare()

    async def index(self, request: Request) -> typing.Any:
        self.farmers = await self.database.users.get_all_users
        return self.templates.TemplateResponse(
            "index.html",
            {"request": request, "name": __import__("api").__name__, "version": __import__("api").__version__, "farmers": self.farmers},
        )

    async def form_submit(self, form: Form = Form()) -> HTMLResponse:
        form = await form.form()
        form = dict(form.__dict__["_dict"])
        message = f"{form['firstname']} {form['lastname']} {form['subject']}"
        num = int(form['phone'])
        res = await self.database.users.add_message(num, message)
        if not res:
            self.logger.log(f"User with phone number: {num} not found", "error")
            return HTMLResponse(content="<script>alert('User not found'); window.location.href = '/';</script>")
        self.logger.log(f"Message sent to user with phone number: {num}", "info")
        return HTMLResponse(content="<html><body><h1>Message sent</h1></body></html>")

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
        self.app.add_route("/form_submit", self.form_submit, methods=["POST"])

    @property
    def get_app(self) -> FastAPI:
        return self.app

    @property
    def up(self) -> datetime.datetime:
        return self.uptime

    def run(self, *_args: typing.Optional[typing.Any], **_kwargs: typing.Optional[typing.Any]) -> None:
        uvicorn.run(self.app, debug=True)
