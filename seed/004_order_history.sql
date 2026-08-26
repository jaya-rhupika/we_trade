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
        'order-001',
        'acct-001',
        'AAPL',
        'buy',
        'Finished',
        100,
        150.0000,
        '2026-08-20 09:30:00',
        'market'
    ),

    -- Finished BUY: 50 AAPL @ 160
    -- Combined with order-001 => avg price = 153.3333
    (
        'order-002',
        'acct-001',
        'AAPL',
        'buy',
        'Finished',
        50,
        160.0000,
        '2026-08-20 10:15:00',
        'limit'
    ),

    -- Finished SELL: 30 AAPL @ 170
    -- Leaves 120 AAPL.
    (
        'order-003',
        'acct-001',
        'AAPL',
        'sell',
        'Finished',
        30,
        170.0000,
        '2026-08-21 11:00:00',
        'limit'
    ),

    -- Finished BUY: 20 MSFT with multiple executions
    (
        'order-004',
        'acct-001',
        'MSFT',
        'buy',
        'Finished',
        20,
        400.0000,
        '2026-08-21 13:00:00',
        'market'
    ),

    -- Pending order
    (
        'order-005',
        'acct-001',
        'TSLA',
        'buy',
        'pending',
        10,
        300.0000,
        '2026-08-22 09:00:00',
        'limit'
    ),

    -- Cancelled order
    (
        'order-006',
        'acct-001',
        'QQQ',
        'buy',
        'cancelled',
        25,
        450.0000,
        '2026-08-22 10:00:00',
        'limit'
    ),

    -- Rejected order
    (
        'order-007',
        'acct-001',
        'TSLA',
        'buy',
        'rejected',
        1000,
        300.0000,
        '2026-08-22 10:30:00',
        'market'
    ),


    -- --------------------------------------------------------
    -- acct-002
    -- Almost no cash
    -- --------------------------------------------------------

    -- Finished BUY with low-priced instrument
    -- Deliberately demonstrates account with tiny remaining balance.
    (
        'order-008',
        'acct-002',
        'OLD',
        'buy',
        'Finished',
        10,
        10.0000,
        '2026-07-10 10:00:00',
        'limit'
    ),

    -- Rejected order because an application layer could reject
    -- an order from an account without sufficient cash.
    (
        'order-009',
        'acct-002',
        'AAPL',
        'buy',
        'rejected',
        100,
        200.0000,
        '2026-08-20 14:00:00',
        'market'
    ),


    -- --------------------------------------------------------
    -- acct-003
    -- Suspended account
    -- --------------------------------------------------------

    -- Historical completed order before suspension.
    (
        'order-010',
        'acct-003',
        'SPY',
        'buy',
        'Finished',
        50,
        500.0000,
        '2026-06-01 10:00:00',
        'market'
    ),

    -- Pending order demonstrates order existing while account
    -- is suspended.
    (
        'order-011',
        'acct-003',
        'MSFT',
        'buy',
        'pending',
        5,
        400.0000,
        '2026-08-22 15:00:00',
        'limit'
    ),


    -- --------------------------------------------------------
    -- acct-004
    -- Closed account
    -- --------------------------------------------------------

    -- Historical completed order before account closure.
    (
        'order-012',
        'acct-004',
        'MSFT',
        'buy',
        'Finished',
        10,
        300.0000,
        '2026-01-15 10:00:00',
        'market'
    ),

    -- Historical sale leaving zero holdings.
    (
        'order-013',
        'acct-004',
        'MSFT',
        'sell',
        'Finished',
        10,
        350.0000,
        '2026-02-01 11:00:00',
        'market'
    ),


    -- --------------------------------------------------------
    -- acct-005
    -- ETF investor
    -- --------------------------------------------------------

    -- BUY SPY
    (
        'order-014',
        'acct-005',
        'SPY',
        'buy',
        'Finished',
        100,
        500.0000,
        '2026-08-18 10:00:00',
        'market'
    ),

    -- Second SPY purchase
    (
        'order-015',
        'acct-005',
        'SPY',
        'buy',
        'Finished',
        50,
        520.0000,
        '2026-08-19 10:00:00',
        'limit'
    ),

    -- Partial SELL:
    -- order requests 80 but only 50 executed.
    (
        'order-016',
        'acct-005',
        'SPY',
        'sell',
        'pending',
        80,
        530.0000,
        '2026-08-22 12:00:00',
        'limit'
    ),

    -- QQQ completed purchase
    (
        'order-017',
        'acct-005',
        'QQQ',
        'buy',
        'Finished',
        20,
        450.0000,
        '2026-08-20 12:00:00',
        'limit'
    ),


    -- --------------------------------------------------------
    -- acct-006
    -- No holdings
    -- --------------------------------------------------------

    -- Cancelled order
    (
        'order-018',
        'acct-006',
        'AAPL',
        'buy',
        'cancelled',
        5,
        190.0000,
        '2026-08-22 09:00:00',
        'limit'
    );