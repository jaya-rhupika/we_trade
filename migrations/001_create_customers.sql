<<<<<<< HEAD
CREATE TABLE customer (
    customer_id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dob DATE NOT NULL,
    email VARCHAR(320) NOT NULL UNIQUE,
    password_hashed VARCHAR(255) NOT NULL
);
=======
create type account_state as enum ('active', 'suspended', 'closed');
CREATE TABLE account (
    account_id VARCHAR(255) PRIMARY KEY,
    customer_id UUID NOT NULL,
    balance DECIMAL(19, 4) NOT NULL DEFAULT 0,
    state account_state NOT NULL,
    version INT NOT NULL DEFAULT 1,
>>>>>>> 793b2e413d5a5e39fdf567b0d602b3bace8f48d9

ALTER TABLE account
    ADD CONSTRAINT fk_account_customer
    FOREIGN KEY (customer_id)
    REFERENCES customer (customer_id);

CREATE UNIQUE INDEX uq_account_customer_id
    ON account (customer_id);