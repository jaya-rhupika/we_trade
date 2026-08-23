CREATE TABLE holdings (
    account_id VARCHAR(255) NOT NULL,
    ticker_symbol VARCHAR(50) NOT NULL,
    avg_price_paid DECIMAL(19, 4) NOT NULL,
    units DECIMAL(19, 4) NOT NULL,

    PRIMARY KEY (account_id, ticker_symbol),

    CONSTRAINT fk_holdings_account
        FOREIGN KEY (account_id)
        REFERENCES account (account_id),

    CONSTRAINT fk_holdings_instrument
        FOREIGN KEY (ticker_symbol)
        REFERENCES instrument (ticker_symbol),

    CONSTRAINT chk_holdings_avg_price
        CHECK (avg_price_paid >= 0),

    CONSTRAINT chk_holdings_units
        CHECK (units >= 0)
);