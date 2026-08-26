-- ============================================================
-- 1. GET ALL HOLDINGS FOR A SPECIFIC CUSTOMER
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
LIMIT 10;


-- ============================================================
-- 3. RANK ORDERS FOR AN ACCOUNT BY ORDER VALUE
-- ============================================================
--
-- PURPOSE:
-- Ranks the finished orders of an account based on their
-- total order value (units × unit price).
--
-- WINDOW FUNCTION:
-- RANK() is used so that every order remains as an individual
-- row while also receiving a rank.
--
-- INDEX:
-- No additional index is specifically required for the
-- RANK() operation itself.
--
-- The existing idx_orders_account_time can help PostgreSQL
-- locate rows belonging to the requested account, but it does
-- NOT directly optimize the ranking because the ranking is
-- performed using a calculated value:
--
--     no_of_units * unit_price
--
-- There is no index on this calculated expression in the
-- current design.
--
-- WHY WE DON'T ADD AN INDEX:
-- Creating an index specifically for this analytical calculation
-- would add write/storage overhead and is not justified for a
-- normal application query.
--
-- This is a good example where an index is NOT necessary.


SELECT
    account_id,
    order_id,
    ticker_symbol,
    order_side,
    no_of_units,
    unit_price,
    no_of_units * unit_price AS order_value,
    RANK() OVER (
        PARTITION BY account_id
        ORDER BY no_of_units * unit_price DESC
    ) AS order_rank
FROM order_history
WHERE account_id = 'acct-001'
  AND order_status = 'Finished';


-- ============================================================
-- 4. GET CUSTOMERS WHO HOLD MORE THAN A CERTAIN NUMBER
--    OF UNITS OF A SPECIFIC INSTRUMENT
-- ============================================================
--
-- PURPOSE:
-- Finds customers who own more than 50 units of AAPL.
--
-- SUBQUERY:
-- The subquery first finds the customer IDs of accounts
-- that hold more than 50 AAPL units.
-- The outer query then retrieves those customers' details.
--
-- INDEXES USED:
-- 1. holdings(account_id, ticker_symbol)
--    PRIMARY KEY.
--
--    This is useful for locating holdings for a particular
--    account, but it is NOT ideal for searching by ticker_symbol
--    alone because ticker_symbol is the second column.
--
-- 2. idx_holdings_ticker
--    ON holdings(ticker_symbol)
--
--    This index directly supports the ticker_symbol filter.
--
-- WHY idx_holdings_ticker IS USEFUL:
-- Without it, PostgreSQL may have to scan the holdings table
-- to find every AAPL holding.
--
-- TRADE-OFF:
-- The index requires additional disk space and must be updated
-- whenever a holding is inserted, deleted, or its ticker changes.
--
-- If the application never searches holdings by ticker_symbol,
-- this index can be removed. It is mainly useful for queries
-- such as this one and for reporting/analytics.
--
-- NOTE:
-- The PK index on holdings already handles the JOIN from
-- account_id, so we don't need another account_id index.


SELECT
    customer_id,
    name,
    email
FROM customer
WHERE customer_id IN (
    SELECT a.customer_id
    FROM account a
    JOIN holdings h
        ON a.account_id = h.account_id
    WHERE h.ticker_symbol = 'AAPL'
      AND h.units > 50
);


-- ============================================================
-- 5. GET TOTAL EXECUTED UNITS AND AVERAGE EXECUTION PRICE
-- ============================================================
--
-- PURPOSE:
-- Calculates how many units of an order were actually executed
-- and the volume-weighted average execution price.
--
-- For example:
--
-- 12 units @ 395
--  8 units @ 405
--
-- Average execution price:
--
-- (12 × 395 + 8 × 405) / 20 = 399
--
-- INDEX USED:
-- idx_execution_order
-- ON execution(order_id, executed_at DESC)
--
-- WHY THE INDEX IS USEFUL:
-- The query searches for executions belonging to one order.
-- order_id is therefore the important lookup column.
--
-- The composite index also stores executed_at, which is useful
-- for queries that retrieve executions in chronological order.
--
-- WITHOUT THE INDEX:
-- PostgreSQL may scan the entire execution table to find the
-- executions belonging to the requested order.
--
-- TRADE-OFF:
-- Every execution INSERT must update this index and the index
-- consumes additional storage.
--
-- Since viewing/calculating executions for an order is a core
-- trading application operation, this is a worthwhile trade-off.


SELECT
    e.order_id,
    SUM(e.units) AS total_executed_units,
    SUM(e.units * e.execution_price)
        / NULLIF(SUM(e.units), 0) AS average_execution_price
FROM execution e
WHERE e.order_id = 'order-004'
GROUP BY e.order_id;


-- ============================================================
-- 6. GET ALL PENDING ORDERS WITH CUSTOMER AND INSTRUMENT DETAILS
-- ============================================================
--
-- PURPOSE:
-- Retrieves all pending orders along with the customer,
-- account, and instrument information.
--
-- This could be useful for an internal trading/operations
-- dashboard.
--
-- INDEXES:
-- idx_orders_account_time is NOT particularly useful here
-- because the query does not filter by account_id.
--
-- There is currently no index on order_status.
--
-- WHY WE DON'T CREATE AN ORDER_STATUS INDEX:
-- If most orders have common statuses such as Finished,
-- pending, cancelled, etc., an index on order_status may not
-- be selective enough to justify its maintenance cost.
--
-- PostgreSQL may choose a sequential scan instead.
--
-- The PK indexes on account_id, customer_id and ticker_symbol
-- help the JOIN lookups once the relevant order rows are found.
--
-- This is another example where creating an index is not
-- automatically beneficial just because a column appears in
-- a WHERE clause.


SELECT
    o.order_id,
    a.account_id,
    c.name AS customer_name,
    i.ticker_symbol,
    i.instrument_name,
    o.order_side,
    o.no_of_units,
    o.unit_price,
    o.order_type,
    o.time
FROM order_history o
JOIN account a
    ON o.account_id = a.account_id
JOIN customer c
    ON a.customer_id = c.customer_id
JOIN instrument i
    ON o.ticker_symbol = i.ticker_symbol
WHERE o.order_status = 'pending'
ORDER BY o.time DESC;


-- ============================================================
-- 7. GET EXECUTION DETAILS FOR A SPECIFIC ORDER
-- ============================================================
--
-- PURPOSE:
-- Displays the order information together with every execution
-- (fill) associated with that order.
--
-- APPLICATION USE:
-- This could be used when the customer opens:
--
--     Order → View Details
--
-- INDEX USED:
-- idx_execution_order
-- ON execution(order_id, executed_at DESC)
--
-- The order_history.order_id is a PRIMARY KEY and therefore
-- already has an index.
--
-- Therefore:
--
--     order_history → execution
--
-- can efficiently find the specific order and its executions.
--
-- The execution index is particularly important because one
-- order can have multiple executions.
--
-- WITHOUT THE EXECUTION INDEX:
-- PostgreSQL may need to scan the entire execution table to
-- find executions belonging to the requested order.
--
-- TRADE-OFF:
-- Additional storage and a small write overhead whenever a
-- new execution is inserted.
--
-- No separate index on order_history(order_id) is necessary
-- because order_id is already the PRIMARY KEY.


SELECT
    o.order_id,
    o.ticker_symbol,
    o.order_side,
    o.order_status,
    o.no_of_units AS ordered_units,
    o.unit_price AS order_price,
    e.execution_id,
    e.units AS executed_units,
    e.execution_price,
    e.executed_at
FROM order_history o
JOIN execution e
    ON o.order_id = e.order_id
WHERE o.order_id = :order_id
ORDER BY e.executed_at;


-- ============================================================
-- 8. CUMULATIVE UNITS FOR EACH ACCOUNT AND TICKER OVER TIME
-- ============================================================
--
-- PURPOSE:
-- Shows the cumulative number of units traded for each
-- account + ticker combination over time.
--
-- WINDOW FUNCTION:
-- SUM() OVER() is used with:
--
--     PARTITION BY account_id, ticker_symbol
--
-- This creates a separate cumulative calculation for every
-- account/instrument combination.
--
-- Example:
--
-- acct-001 / AAPL:
--
-- 100 → cumulative 100
--  50 → cumulative 150
--  30 → cumulative 180
--
-- IMPORTANT:
-- This query calculates CUMULATIVE TRADED UNITS.
-- Because both BUY and SELL units are positive, a SELL adds
-- to the cumulative total.
--
-- If the goal is NET HOLDINGS, SELL units should instead be
-- subtracted using CASE:
--
--     BUY  → +units
--     SELL → -units
--
-- INDEX:
-- No additional index is specifically required for the
-- window calculation.
--
-- The existing indexes may help locate/filter rows, but the
-- database still needs to process the rows in account/ticker/time
-- order for the window function.
--
-- Creating an index specifically for this analytical query is
-- not necessary for the current application because this is
-- more of an analytical/reporting operation.
--
-- TRADE-OFF:
-- An additional composite index could speed up some versions
-- of this query but would increase storage and write overhead.
-- Therefore we avoid adding it unless this becomes a frequent
-- production query.


SELECT
    account_id,
    ticker_symbol,
    order_id,
    time,
    no_of_units,

    SUM(no_of_units) OVER (
        PARTITION BY account_id, ticker_symbol
        ORDER BY time
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_units

FROM order_history
WHERE order_status = 'Finished'
ORDER BY account_id, ticker_symbol, time;