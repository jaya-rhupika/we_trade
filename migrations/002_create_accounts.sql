<<<<<<< HEAD
create type account_state as enum ('active', 'suspended', 'closed');
CREATE TABLE account (
    account_id VARCHAR(255) PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    balance DECIMAL(19, 4) NOT NULL DEFAULT 0,
    state account_state NOT NULL,
    version INT NOT NULL DEFAULT 1,
=======
CREATE TABLE customer (
    customer_id UUID PRIMARY KEY,
    name VARCHAR(255),
    dob DATE,
    email VARCHAR(255),
    password_hashed VARCHAR(255)
);
>>>>>>> 793b2e413d5a5e39fdf567b0d602b3bace8f48d9

    CONSTRAINT chk_account_balance
        CHECK (balance >= 0),

    CONSTRAINT chk_account_version
        CHECK (version > 0)
);