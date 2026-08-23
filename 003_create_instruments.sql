create type instrument_category as enum ('stock', 'etf');
create type instrument_status as enum ('active', 'delisted', 'halted');
CREATE TABLE instrument (
    ticker_symbol VARCHAR(50) PRIMARY KEY,
    instrument_name VARCHAR(255) NOT NULL,
    currency VARCHAR(10) NOT NULL,
    category instrument_category NOT NULL,
    status instrument_status NOT NULL
);