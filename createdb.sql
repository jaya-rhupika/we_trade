create type account_state as enum ('active', 'suspended', 'closed');
create type instrument_category as enum ('stock', 'etf');
create type instrument_status as enum ('active', 'delisted', 'halted');
create type order_side as enum ('buy', 'sell');
create type order_status as enum ('pending', 'Finished', 'cancelled', 'rejected');
create type order_type as enum ('market', 'limit');

-- 1. customer table
create table customer (
    customer_id UUID,
    name varchar(255) not null,
    dob date not null,
    email varchar(255) not null,
    password_hashed varchar(255) not null,
    constraint pk_customer primary key (customer_id),
    constraint uk_customer_email unique (email)
);

-- 2. account table
create table account (
    account_id int ,
    customer_id UUID not null,
    balance decimal(15, 2) not null default 0.00,
    state account_state not null,
    version int not null default 1,
    constraint pk_account primary key (account_id),
    constraint fk_account_customer foreign key (customer_id) 
        references customer(customer_id) on delete cascade
);

-- 3. instrument table
create table instrument (
    ticker_symbol varchar(50) not null,
    instrument_name varchar(255) not null,
    currency varchar(10) not null,
    category instrument_category not null,
    status instrument_status not null,
    constraint pk_instrument primary key (ticker_symbol)
);

-- 4. order_history table
create table order_history (
    order_id int,
    account_id int not null,
    ticker_symbol varchar(50) not null,
    order_side order_side not null,
    order_status order_status not null,
    no_of_units int not null,
    unit_price decimal(15, 4) not null,
    time timestamp not null default current_timestamp,
    order_type order_type not null,
    constraint pk_order_history primary key (order_id),
    constraint fk_order_history_account foreign key (account_id) 
        references account(account_id),
    constraint fk_order_history_instrument foreign key (ticker_symbol) 
        references instrument(ticker_symbol)
);

-- 5. holdings table 
create table holdings (
    account_id int not null,
    ticker_symbol varchar(50) not null,
    avg_price_paid decimal(15, 4) not null,
    units decimal(15, 4) not null,
    constraint pk_holdings primary key (account_id, ticker_symbol),
    constraint fk_holdings_account foreign key (account_id) 
        references account(account_id) on delete cascade,
    constraint fk_holdings_instrument foreign key (ticker_symbol) 
        references instrument(ticker_symbol)
);

-- 6. idempotency table
create table idempotency (
    idempotency_key varchar(255) not null,
    order_id int not null,
    created_at timestamp not null default current_timestamp,
    constraint pk_idempotency primary key (idempotency_key),
    constraint fk_idempotency_order foreign key (order_id) 
        references order_history(order_id) on delete cascade
);
