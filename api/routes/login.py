from typing import TYPE_CHECKING

import phonenumbers
from fastapi import APIRouter, FastAPI, HTTPException

from api.utils import User

if TYPE_CHECKING:
    from api.setup import Database, Logs


class Login:
    __slots__: tuple[str, ...] = ("database", "logger")
    router: APIRouter = APIRouter()

    def __init__(self, database: "Database", logger: "Logs") -> None:
        self.database = database
        self.logger = logger

    async def validity_check(self, phone_number: int, state: str, district: str) -> bool:
        number = phonenumbers.parse(f"+91{phone_number}")
        if not phonenumbers.is_valid_number(number):
            self.logger.log(f"Invalid phone number: {phone_number}", "error")
            raise HTTPException(status_code=404, detail="Invalid phone number")
        if state not in await self.database.prices.get_all_states:
            self.logger.log(f"Invalid state: {state}", "error")
            raise HTTPException(
                status_code=404, detail=f"Invalid state. Valid states are {', '.join(await self.database.prices.get_all_states)}"
            )
        if district not in await self.database.prices.get_all_districts:
            self.logger.log(f"Invalid district: {district}", "error")
            raise HTTPException(
                status_code=404,
                detail=f"Invalid district. Valid districts are {', '.join(await self.database.prices.get_districts_by_state(state))}",
            )
        return True

    async def get_user(self, phone_number: int) -> User:
        result: User = await self.database.users.get_user(phone_number)
        if not result:
            self.logger.log(f"No user found with that phone number: {phone_number}", "error")
            raise HTTPException(status_code=404, detail="No user found with that phone number")
        self.logger.log(f"Found user with phone number: {phone_number}", "info")
        return result

    async def login(self, phone_number: int, password: str) -> dict[str, bool]:
        result = await self.database.users.login_user(phone_number, password)
        if not result:
            self.logger.log(f"Invalid password for user with phone number: {phone_number}", "error")
            raise HTTPException(status_code=404, detail="Invalid password for user with that phone number")
        self.logger.log(f"User with phone number: {phone_number} logged in", "info")
        return {"found": True}

    async def register(self, phone_number: int, name: str, password: str, state: str, district: str) -> User:
        result = await self.validity_check(phone_number, state, district)
        if not result:
            raise HTTPException(status_code=404, detail="Invalid phone number, state or district")
        user = await self.database.users.get_user(phone_number)
        if user:
            self.logger.log(f"User with phone number: {phone_number} already exists", "error")
            raise HTTPException(status_code=404, detail="User with that phone number already exists")
        await self.database.users.register_user(User(phone_number, name, password, state, district))
        self.logger.log(f"User with phone number: {phone_number} registered", "info")
        return await self.database.users.get_user(phone_number)

    async def update_password(self, phone_number: int, old_password: str, new_password: str) -> User:
        result = await self.database.users.login_user(phone_number, old_password)
        if not result:
            self.logger.log(f"Invalid password for user with phone number: {phone_number}", "error")
            raise HTTPException(status_code=404, detail="Invalid password for user with that phone number")
        await self.database.users.update_password(phone_number, new_password)
        self.logger.log(f"User with phone number: {phone_number} updated password", "info")
        return await self.database.users.get_user(phone_number)

    async def update_location(self, phone_number: int, password: str, state: str, district: str) -> User:
        result = await self.database.users.login_user(phone_number, password)
        if not result:
            self.logger.log(f"Invalid password for user with phone number: {phone_number}", "error")
            raise HTTPException(status_code=404, detail="Invalid password for user with that phone number")
        await self.validity_check(phone_number, state, district)
        await self.database.users.update_state(phone_number, state)
        await self.database.users.update_district(phone_number, district)
        self.logger.log(f"User with phone number: {phone_number} updated location", "info")
        return await self.database.users.get_user(phone_number)        

    async def delete_user(self, phone_number: int) -> None:
        await self.database.users.delete_user(phone_number)
        self.logger.log(f"User with phone number: {phone_number} deleted", "info")
    
    async def all_states(self) -> dict[str, list[str]]:
        states = await self.database.prices.get_all_states
        res = {i: await self.database.prices.get_districts_by_state(i) for i in states}
        return res

    def setup(self) -> None:
        self.router.add_api_route("/register/login", self.login, methods=["GET"], response_model=dict[str, bool])
        self.router.add_api_route("/register/register", self.register, methods=["GET"], response_model=User)
        self.router.add_api_route("/register/update_password", self.update_password, methods=["GET"], response_model=User)
        self.router.add_api_route("/register/update_location", self.update_location, methods=["GET"], response_model=User)
        self.router.add_api_route("/register/delete_user", self.delete_user, methods=["GET"])
        self.router.add_api_route("/register/info", self.get_user, methods=["GET"], response_model=User)
        self.router.add_api_route("/register/reigons", self.all_states, methods=["GET"], response_model=dict[str, list[str]])


async def setup(app: FastAPI, database: "Database", logger: "Logs") -> None:
    login = Login(database, logger)
    login.setup()
    app.include_router(login.router, prefix="/api/v1", tags=["Login"])
    logger.log("Login routes setup complete", "info")
