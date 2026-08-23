CREATE TABLE idempotency (
    idempotency_key UUID PRIMARY KEY,
    order_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL,

    CONSTRAINT fk_idempotency_order
        FOREIGN KEY (order_id)
        REFERENCES order_history (order_id)
);

CREATE INDEX idx_idempotency_order_id
    ON idempotency (order_id);