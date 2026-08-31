CREATE TABLE customer (
    customer_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hashed VARCHAR(255) NOT NULL
);

ALTER TABLE account
    ADD CONSTRAINT fk_account_customer
    FOREIGN KEY (customer_id)
    REFERENCES customer (customer_id);

CREATE UNIQUE INDEX uq_account_customer_id
    ON account (customer_id);