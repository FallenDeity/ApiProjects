import datetime
from dataclasses import dataclass, InitVar

__all__: tuple[str, ...] = ("Price", "Sql", "User", "Production", "Kingdom", "Divisions", "Classes", "Plant")


@dataclass
class Plant:
    common_name: str | None
    scientific_name: str | None
    author: str | None
    description: str | None
    rank: str | None
    family: str | None
    genus: str | None
    image: str | None


@dataclass
class Classes:
    Chlorophyta: list[str]
    Bryophyta: list[str]
    Charophyta: list[str]
    Marchantiophyta: list[str]
    Tracheophyta: list[str]
    Anthocerotophyta: list[str]
    Rhodophyta: list[str]
    Glaucophyta: list[str]
    Myxomycota: list[str]
    Ascomycota: list[str]


@dataclass
class Divisions:
    Viridiplantae: list[str]
    Biliphyta: list[str]
    Eomycota: list[str]
    Dikarya: list[str]


@dataclass
class Kingdom:
    Plantae: list[str]
    Fungi: list[str]


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
    VALUES: InitVar[list[float]]

    def __post_init__(self, values: list[float]) -> None:
        self.VALUES: list[Value] = [Value(int(year), value) for year, value in enumerate(values, start=1993)]


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
