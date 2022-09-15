from dataclasses import dataclass

__all__: tuple[str, ...] = ("SQL",)


@dataclass
class SQL:
    area_to_prices_c: str = """CREATE TABLE IF NOT EXISTS prices (
            ID SERIAL PRIMARY KEY,
            STATE VARCHAR(255) NOT NULL,
            DISTRICT VARCHAR(255) NOT NULL,
            MARKET VARCHAR(255) NOT NULL,
            COMMODITY VARCHAR(255) NOT NULL,
            VARIETY VARCHAR(255) NOT NULL,
            ARRIVAL_DATE VARCHAR(255) NOT NULL,
            MIN_PRICE INTEGER NOT NULL,
            MAX_PRICE INTEGER NOT NULL,
            MODAL_PRICE INTEGER NOT NULL
            )"""
    area_to_prices_i: str = """INSERT INTO prices (STATE, DISTRICT, MARKET, COMMODITY, VARIETY, ARRIVAL_DATE, MIN_PRICE, MAX_PRICE, MODAL_PRICE)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)"""
