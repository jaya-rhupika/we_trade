INSERT INTO order_history (
    order_id,
    account_id,
    ticker_symbol,
    order_side,
    order_status,
    no_of_units,
    unit_price,
    time,
    order_type
) VALUES

    -- --------------------------------------------------------
    -- acct-001
    -- --------------------------------------------------------

    -- Finished BUY: 100 AAPL @ 150
    (
        'order-199',
        'missing account',
        'AAPL',
        'buy',
        'Finished',
        100,
        150.0000,
        '2026-08-20 09:30:00',
        'market'
    )