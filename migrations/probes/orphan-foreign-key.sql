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
    'order-orphan-001',
    'missing-account',
    'orphan-test-key',
    'AAPL',
    'BUY',
    'PENDING',
    'MARKET',
    10,
    150.00
);