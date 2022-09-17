import datetime
from dataclasses import dataclass

__all__: tuple[str, ...] = ("Price", "Sql", "User", "Production")


@dataclass
class Value:
    YEAR: int
    PRODUCE: float


@dataclass
class Production:
    ID: int
    CROP: str
    FREQUENCY: str
    UNIT: str
    VALUES: list[Value]

    def __init__(self, _id: int, crop: str, frequency: str, unit: str, values: list[float]) -> None:
        self.ID = _id
        self.CROP = crop
        self.FREQUENCY = frequency
        self.UNIT = unit
        self.VALUES = [Value(int(year), value) for year, value in enumerate(values, start=1993)]


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
