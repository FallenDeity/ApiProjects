from dataclasses import dataclass


__all__: tuple[str, ...] = ("Price",)


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
