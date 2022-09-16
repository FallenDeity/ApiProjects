from dotenv import load_dotenv

from api.setup import API
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

load_dotenv()
session = API()
templates = Jinja2Templates(directory="api/assets/templates")


@session.app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "name": "AgroIndia", "version": "0.0.1"})

app = session.get_app
session.run()

