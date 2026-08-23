INSERT INTO account (
    account_id,
    customer_id,
    balance,
    state,
    version
) VALUES
    -- Normal active investor
    (
        'acct-001',
        'cust-001',
        12500.0000,
        'active',
        5
    ),

    -- Active account with almost no cash
    (
        'acct-002',
        'cust-002',
        0.0100,
        'active',
        8
    ),

    -- Suspended account
    (
        'acct-003',
        'cust-003',
        7500.0000,
        'suspended',
        3
    ),

    -- Closed account
    (
        'acct-004',
        'cust-004',
        0.0000,
        'closed',
        6
    ),

    -- Active account used for ETF trading
    (
        'acct-005',
        'cust-005',
        25000.0000,
        'active',
        12
    ),

    -- Active account with no holdings
    (
        'acct-006',
        'cust-006',
        5000.0000,
        'active',
        1
    );