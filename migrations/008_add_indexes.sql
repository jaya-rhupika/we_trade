
CREATE INDEX idx_account_customer
ON account(customer_id);

CREATE INDEX idx_orders_account_time
ON order_history(account_id, time DESC);

CREATE INDEX idx_orders_ticker
ON order_history(ticker_symbol);
--not required right now for the application, but will be useful for reporting

CREATE INDEX idx_idempotency_created
ON idempotency(created_at);
--for very large amount of idempotency records

CREATE INDEX idx_holdings_ticker
ON holdings(ticker_symbol);
--again only for reporting

CREATE INDEX idx_execution_order
ON execution(order_id, executed_at DESC);
