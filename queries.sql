
-- ============================================================
-- 1. GET ALL OPEN ORDERS FOR ONE ACCOUNT
-- ============================================================
--
-- PURPOSE:
-- Retrieves all currently open orders for a specific account,
-- with the newest orders appearing first.
--
-- This could be used directly by the order blotter on every
-- dashboard load.
--
-- INDEX USED:
-- idx_orders_account_time
-- ON order_history(account_id, time DESC)
--
-- WHY THIS INDEX IS USEFUL:
-- The query filters using account_id and then sorts by time DESC.
-- The composite index supports both operations efficiently.
--
-- PostgreSQL can locate the rows belonging to the requested
-- account and retrieve them in newest-first order without
-- requiring a separate sort operation.
--
-- TRADE-OFF:
-- The index requires additional disk space and must be updated
-- whenever an order is inserted, deleted, or its account/time
-- values change.
--
-- Since the order blotter is loaded frequently, the read
-- performance benefit justifies the additional write overhead.


SELECT
    o.order_id,
    o.ticker_symbol,
    o.order_side,
    o.order_status,
    o.no_of_units,
    o.unit_price,
    o.order_type,
    o.time
FROM order_history o
WHERE o.account_id = 'acct-001'
  AND o.order_status = 'pending'
ORDER BY o.time DESC;



-- ============================================================
-- 2. GET THE LATEST ORDERS FOR AN ACCOUNT
-- ============================================================
--
-- PURPOSE:
-- Retrieves the most recent orders for an account.
-- This could be used directly by the Order History page.
--
-- INDEX USED:
-- idx_orders_account_time
-- ON order_history(account_id, time DESC)
--
-- WHY THIS INDEX IS USEFUL:
-- The query filters using account_id and then sorts by time DESC.
-- The composite index is already ordered by account_id and then
-- by time in descending order.
--
-- This allows PostgreSQL to efficiently locate the account's
-- orders and retrieve the newest orders first.
--
-- The LIMIT 10 makes this particularly useful because PostgreSQL
-- can stop after finding the first 10 matching rows.
--
-- WITHOUT THE INDEX:
-- PostgreSQL may need to scan many/all rows in order_history,
-- identify rows belonging to the account, sort them by time,
-- and then return 10 rows.
--
-- TRADE-OFF:
-- Every INSERT into order_history must also update this index.
-- The index also consumes additional disk space.
--
-- Since viewing recent orders is a core application operation,
-- this is a worthwhile trade-off.


SELECT
    order_id,
    ticker_symbol,
    order_side,
    order_status,
    no_of_units,
    unit_price,
    time,
    order_type
FROM order_history
WHERE account_id = 'acct-001'
ORDER BY time DESC
LIMIT 50;


-- ============================================================
-- 3. GET ALL HOLDINGS FOR A SPECIFIC CUSTOMER
-- ============================================================
--
-- PURPOSE:
-- Retrieves a customer's complete portfolio along with
-- instrument details such as name and category.
--
-- RELATIONSHIP:
-- Customer → Account → Holdings → Instrument
--
-- INDEXES USED:
-- 1. account.customer_id
--    idx_account_customer
--    Helps find the account belonging to the specified customer.
--
-- 2. holdings(account_id, ticker_symbol)
--    This is the PRIMARY KEY of holdings, so PostgreSQL already
--    has an index for it.
--    It efficiently finds holdings belonging to an account.
--
-- 3. instrument.ticker_symbol
--    This is the PRIMARY KEY, so it is automatically indexed.
--
-- WHY THE INDEXES MATTER:
-- Without the account.customer_id index, PostgreSQL may need to
-- scan the account table to find the customer's account.
--
-- The PK indexes on holdings and instrument already support
-- the JOIN operations, so no additional indexes are required.
--
-- TRADE-OFF:
-- idx_account_customer adds storage and slightly increases the
-- cost of INSERT/UPDATE/DELETE operations on the account table.
-- However, finding an account by customer_id is a common operation,
-- so the read-performance benefit justifies the cost.


SELECT
    c.customer_id,
    c.name,
    a.account_id,
    h.ticker_symbol,
    i.instrument_name,
    i.category,
    h.units,
    h.avg_price_paid
FROM customer c
JOIN account a
    ON c.customer_id = a.customer_id
JOIN holdings h
    ON a.account_id = h.account_id
JOIN instrument i
    ON h.ticker_symbol = i.ticker_symbol
WHERE c.customer_id = 'cust-001';

-- ============================================================
-- 4. GET ALL ORDERS CREATED SINCE A GIVEN TIMESTAMP
-- ============================================================
--
-- PURPOSE:
-- Retrieves every order created since a specified timestamp,
-- across all accounts.
--
-- This could be used by the nightly extract into the
-- analytical store in Sprint 7.
--
-- INDEX:
-- idx_orders_account_time is NOT particularly useful here
-- because the query does not filter by account_id.
--
-- The query filters directly on the time column, but the
-- current design does not contain an index specifically on
-- order_history(time).
--
-- WHY WE DON'T ADD A TIME INDEX:
-- The current application queries do not otherwise require
-- searching the entire order_history table by time alone.
-- Adding an index would introduce additional storage and
-- write-maintenance overhead.
--
--
-- TRADE-OFF:
-- Without a time index, PostgreSQL may scan the order_history
-- table to identify orders created after the specified
-- timestamp.
--
-- This is acceptable for the current application design,
-- although a dedicated time index could be considered if
-- incremental analytical extraction becomes frequent.


SELECT
    order_id,
    account_id,
    ticker_symbol,
    order_side,
    order_status,
    no_of_units,
    unit_price,
    order_type,
    time
FROM order_history
WHERE time >= '2026-01-01 00:00:00'
ORDER BY time ASC;

-- ============================================================
-- 5. RESOLVE AN ACCOUNT FROM A CUSTOMER REFERENCE
-- ============================================================
--
-- PURPOSE:
-- Resolves the account belonging to a specific customer-facing
-- customer reference.
--
-- This could be used by Support when identifying an account
-- from a reference quoted by a customer, and by the auth
-- service during sign-in.
--
-- INDEX USED:
-- account.customer_id
-- idx_account_customer
--
-- WHY THIS INDEX IS USEFUL:
-- The query searches the account table using customer_id.
-- The idx_account_customer index allows PostgreSQL to locate
-- the customer's account without scanning the entire account
-- table.
--
-- TRADE-OFF:
-- The index requires additional storage and introduces a small
-- write overhead whenever an account is inserted, deleted,
-- or its customer_id changes.
--
-- Since account resolution is a frequent application operation,
-- the read-performance benefit justifies the additional cost.


SELECT
    a.account_id,
    a.customer_id
FROM account a
WHERE a.customer_id = 'cust-001';

-- ============================================================
-- 6. GET FILLED ORDERS WITH RUNNING CASH COMMITTED
--     AND RANK BY VALUE WITHIN INSTRUMENT
-- ============================================================
--
-- PURPOSE:
-- Retrieves every filled order for one account in chronological
-- order, calculates the running total of cash committed, and
-- ranks each order by value within its instrument.
--
-- This could be used by the monthly statement.
--
--
-- INDEX USED:
-- idx_orders_account_time
-- ON order_history(account_id, time DESC)
--
-- WHY THIS INDEX IS USEFUL:
-- The query filters by account_id, so the account portion of
-- the composite index helps locate the account's orders.
--
-- The index is ordered by time DESC, while this query presents
-- the results oldest first. PostgreSQL can scan the index in
-- the reverse direction for the time ordering.
--
--
-- TRADE-OFF:
-- The existing account/time index helps identify the relevant
-- orders, but it does not directly optimize the calculated
-- order value or the window functions.
--
-- Creating additional indexes specifically for these calculated
-- values would increase storage and write overhead and is not
-- justified for this monthly reporting query.


SELECT
    account_id,
    order_id,
    ticker_symbol,
    order_side,
    no_of_units,
    unit_price,
    time,

    no_of_units * unit_price AS order_value,

    SUM(no_of_units * unit_price) OVER (
        PARTITION BY account_id
        ORDER BY time, order_id
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_cash_committed,

    RANK() OVER (
        PARTITION BY account_id, ticker_symbol
        ORDER BY no_of_units * unit_price DESC
    ) AS instrument_order_rank

FROM order_history
WHERE account_id = 'acct-001'
  AND order_status = 'Finished'
ORDER BY time ASC, order_id ASC;
