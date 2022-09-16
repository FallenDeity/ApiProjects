import typing

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


from api.setup import API

load_dotenv()
session = API()
templates = Jinja2Templates(directory="api/assets/templates")


@session.app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> typing.Any:
    return templates.TemplateResponse("index.html", {"request": request, "name": "AgroIndia", "version": "0.0.1"})


app = session.get_app

if __name__ == "__main__":
    session.run()
