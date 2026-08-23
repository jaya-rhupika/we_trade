create type order_side as enum ('buy', 'sell');
create type order_status as enum ('pending', 'Finished', 'cancelled', 'rejected');
create type order_type as enum ('market', 'limit');
CREATE TABLE order_history (
    order_id VARCHAR(255) PRIMARY KEY,
    account_id VARCHAR(255) NOT NULL,
    ticker_symbol VARCHAR(50) NOT NULL,
    order_side order_side NOT NULL,
    order_status order_status NOT NULL,
    no_of_units INT NOT NULL,
    unit_price DECIMAL(19, 4) NOT NULL,
    time TIMESTAMP NOT NULL,
    order_type order_type NOT NULL,

    CONSTRAINT fk_order_history_account
        FOREIGN KEY (account_id)
        REFERENCES account (account_id),

    CONSTRAINT fk_order_history_instrument
        FOREIGN KEY (ticker_symbol)
        REFERENCES instrument (ticker_symbol),

    CONSTRAINT chk_order_history_units
        CHECK (no_of_units > 0),

    CONSTRAINT chk_order_history_unit_price
        CHECK (unit_price >= 0)
);

CREATE INDEX idx_order_history_account_id
    ON order_history (account_id);

CREATE INDEX idx_order_history_ticker_symbol
    ON order_history (ticker_symbol);

CREATE INDEX idx_order_history_time
    ON order_history (time);