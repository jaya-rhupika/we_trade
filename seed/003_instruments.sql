INSERT INTO instrument (
    ticker_symbol,
    instrument_name,
    currency,
    category,
    status
) VALUES
    -- Active stocks
    (
        'AAPL',
        'Apple Inc.',
        'USD',
        'stock',
        'active'
    ),
    (
        'MSFT',
        'Microsoft Corporation',
        'USD',
        'stock',
        'active'
    ),
    (
        'TSLA',
        'Tesla Inc.',
        'USD',
        'stock',
        'active'
    ),

    -- Active ETFs
    (
        'SPY',
        'SPDR S&P 500 ETF Trust',
        'USD',
        'etf',
        'active'
    ),
    (
        'QQQ',
        'Invesco QQQ Trust',
        'USD',
        'etf',
        'active'
    ),

    -- Halted instrument
    (
        'XYZ',
        'XYZ Technologies Inc.',
        'USD',
        'stock',
        'halted'
    ),

    -- Delisted instrument
    (
        'OLD',
        'Old Industries Corporation',
        'USD',
        'stock',
        'delisted'
    );