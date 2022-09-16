import datetime
from dataclasses import dataclass

__all__: tuple[str, ...] = ("Price", "Sql", "User")


@dataclass(frozen=True)
class Price:
    ID: int
    STATE: str
    DISTRICT: str
    MARKET: str
    COMMODITY: str
    VARIETY: str
    ARRIVAL_DATE: str
    MIN_PRICE: int
    MAX_PRICE: int
    MODAL_PRICE: int


@dataclass(frozen=True)
class Sql:
    create: str
    insert: str
    update: str = ""


@dataclass(frozen=True)
class User:
    phone: int
    name: str
    password: str
    state: str
    district: str
    created_at: float = datetime.datetime.now().timestamp()
