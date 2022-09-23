import asyncio
import json
import math
import os
import typing
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from typing import TYPE_CHECKING

import aiofiles
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, FastAPI

from api.utils import Classes, Divisions, Kingdom, Plant

if TYPE_CHECKING:
    from api.setup import Database, Logs


class Encyclopedia:

    __slots__: tuple[str, ...] = ("database", "logger")
    router: APIRouter = APIRouter()
    ENCYCLOPEDIA_ID: str = os.getenv("ENCYCLOPEDIA_ID")
    ENDPOINT: str = "https://api.floracodex.com/v1/"

    def __init__(self, database: "Database", logger: "Logs") -> None:
        self.database = database
        self.logger = logger

    @staticmethod
    def parser(holder: list, data: dict[str, typing.Any]) -> None:
        desc = requests.get(
            f"https://en.wikipedia.org/wiki/{data.get('scientific_name').replace(' ', '_').capitalize()}")
        if desc.status_code != 200:
            desc = requests.get(
                f"https://en.wikipedia.org/wiki/{data.get('common_name').replace(' ', '_').capitalize()}")
        soup = BeautifulSoup(desc.text, "html.parser")
        try:
            description = (
                "".join([i.text for i in soup.find_all("p") if i.text][:7])
                if desc.status_code == 200
                else "No description found."
            )
        except AttributeError:
            description = "No description found."
        holder.append(
            Plant(
                **{
                    "common_name": data.get("common_name"),
                    "scientific_name": data.get("scientific_name"),
                    "author": data.get("author"),
                    "description": f"{description}... [{desc.url}]",
                    "rank": data.get("rank"),
                    "family": data.get("family"),
                    "genus": data.get("genus"),
                    "image": data.get("image_url"),
                }
            )
        )

    @staticmethod
    def processor(data: list[dict[str, typing.Any]]) -> list[Plant]:
        holder: list[Plant] = []
        with ThreadPoolExecutor(max_workers=10) as pool:
            pool.map(partial(Encyclopedia.parser, holder), data)
        return holder

    @staticmethod
    def parse_kingdoms(data: dict[str, typing.Any]) -> Kingdom:
        holder: dict[str, list[str]] = {}
        for kingdom in data["data"]:
            holder.setdefault(kingdom["kingdom"]["name"], []).append(kingdom["name"])
        return Kingdom(**holder)

    @staticmethod
    def parse_divisions(data: dict[str, typing.Any]) -> Divisions:
        holder: dict[str, list[str]] = {}
        for division in data["data"]:
            sinfo = division["subKingdom"].get("name")
            kinfo = division["subKingdom"]["kingdom"].get("name")
            final = sinfo or kinfo
            holder.setdefault("Eomycota" if final == "Fungi" else final, []).append(division["name"])
        return Divisions(**holder)

    @staticmethod
    def parse_classes(data: dict[str, typing.Any]) -> Classes:
        holder: dict[str, list[str]] = {}
        for class_ in data["data"]:
            holder.setdefault(class_["division"]["name"], []).append(class_["name"])
        return Classes(**holder)

    @staticmethod
    def parse_orders(data: dict[str, typing.Any]) -> dict[str, list[str]]:
        holder: dict[str, list[str]] = {}
        for order in data["data"]:
            iname = order["division_class"].get("name") or order["division_class"]["division"].get("name")
            holder.setdefault(iname, []).append(order["name"])
        return holder

    async def get_len(self, word: str, queries: str = "") -> tuple[dict, int]:
        response = await self.database.client.get(f"{self.ENDPOINT}{word}?key={self.ENCYCLOPEDIA_ID}{queries}")
        data = await response.json()
        total = math.ceil(data["meta"]["total"] / len(data["data"]))
        return data, total

    async def kingdoms(self) -> Kingdom:
        response = await self.database.client.get(f"{self.ENDPOINT}subkingdoms?key={self.ENCYCLOPEDIA_ID}")
        return self.parse_kingdoms(await response.json())

    async def divisions(self) -> Divisions:
        response = await self.database.client.get(f"{self.ENDPOINT}divisions?key={self.ENCYCLOPEDIA_ID}")
        return self.parse_divisions(await response.json())

    async def classes(self) -> Classes:
        data, total = await self.get_len("division_classes")
        for i in range(1, total):
            response = await self.database.client.get(f"{self.ENDPOINT}division_classes?key={self.ENCYCLOPEDIA_ID}&page={i}")
            data["data"].extend((await response.json())["data"])
        return self.parse_classes(data)

    async def orders(self) -> dict[str, list[str]]:
        data, total = await self.get_len("division_orders")
        for i in range(1, total):
            response = await self.database.client.get(f"{self.ENDPOINT}division_orders?key={self.ENCYCLOPEDIA_ID}&page={i}")
            data["data"].extend((await response.json())["data"])
        return self.parse_orders(data)

    @staticmethod
    async def families() -> dict[str, list[str]] | None:
        file = "api/bin/bio/families.json"
        async with aiofiles.open(file, "r") as f:
            data: dict[str, list[str]] = json.loads(await f.read())
        return data

    @staticmethod
    async def genus() -> dict[str, list[str]]:
        file = "api/bin/bio/genus.json"
        async with aiofiles.open(file, "r") as f:
            data: dict[str, list[str]] = json.loads(await f.read())
        return data

    async def search_plant(self, query: str) -> list[Plant]:
        data, total = await self.get_len("plants/search", f"&q={query}")
        for i in range(1, total):
            response = await self.database.client.get(
                f"{self.ENDPOINT}plants/search?key={self.ENCYCLOPEDIA_ID}&page={i}&q={query}"
            )
            data["data"].extend((await response.json())["data"])
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, partial(self.processor, [i for i in data["data"] if i["rank"] == "SPECIES"]))

    def setup(self) -> None:
        self.router.add_api_route("/encyclopedia/kingdoms", self.kingdoms, methods=["GET"], response_model=Kingdom)
        self.router.add_api_route("/encyclopedia/divisions", self.divisions, methods=["GET"], response_model=Divisions)
        self.router.add_api_route("/encyclopedia/classes", self.classes, methods=["GET"], response_model=Classes)
        self.router.add_api_route("/encyclopedia/orders", self.orders, methods=["GET"], response_model=dict[str, list[str]])
        self.router.add_api_route("/encyclopedia/families", self.families, methods=["GET"], response_model=dict[str, list[str]])
        self.router.add_api_route("/encyclopedia/genus", self.genus, methods=["GET"], response_model=dict[str, list[str]])
        self.router.add_api_route("/encyclopedia/search", self.search_plant, methods=["GET"], response_model=list[Plant])


async def setup(app: FastAPI, database: "Database", logger: "Logs") -> None:
    encyclopedia = Encyclopedia(database, logger)
    encyclopedia.setup()
    app.include_router(encyclopedia.router, prefix="/api/v1", tags=["Encyclopedia"])
    logger.log("Encyclopedia routes loaded", "info")
