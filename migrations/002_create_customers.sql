CREATE TABLE customer (
    customer_id UUID PRIMARY KEY,
    name VARCHAR(255),
    dob DATE,
    email VARCHAR(255),
    password_hashed VARCHAR(255)
);

ALTER TABLE account
    ADD CONSTRAINT fk_account_customer
    FOREIGN KEY (customer_id)
    REFERENCES customer (customer_id);

CREATE UNIQUE INDEX uq_account_customer_id
    ON account (customer_id);