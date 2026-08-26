INSERT INTO account (
    account_id,
    state
)
VALUES (
    'account-001',
    'ACTIVE'
);


INSERT INTO orders (
    order_id,
    account_id,
    idempotency_key,
    ticker_symbol,
    order_side,
    order_status,
    order_type,
    no_of_units,
    unit_price
)
VALUES (
    'order-001',
    'account-001',
    'duplicate-key-test',
    'AAPL',
    'BUY',
    'PENDING',
    'MARKET',
    10,
    150.00
);


INSERT INTO orders (
    order_id,
    account_id,
    idempotency_key,
    ticker_symbol,
    order_side,
    order_status,
    order_type,
    no_of_units,
    unit_price
)
VALUES (
    'order-002',
    'account-001',
    'duplicate-key-test',
    'AAPL',
    'BUY',
    'PENDING',
    'MARKET',
    5,
    150.00
);