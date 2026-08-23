CREATE TABLE execution (
    execution_id VARCHAR(255) PRIMARY KEY,
    order_id VARCHAR(255) NOT NULL,
    units DECIMAL(19, 4) NOT NULL,
    execution_price DECIMAL(19, 4) NOT NULL,
    executed_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_execution_order
        FOREIGN KEY (order_id)
        REFERENCES order_history (order_id),

    CONSTRAINT chk_execution_units
        CHECK (units > 0),

    CONSTRAINT chk_execution_price
        CHECK (execution_price >= 0)
);

CREATE INDEX idx_execution_order_id
    ON execution (order_id);

CREATE INDEX idx_execution_executed_at
    ON execution (executed_at);