
CREATE SCHEMA target;

-- User Table
CREATE TABLE target."user" (
    user_id VARCHAR(32) PRIMARY KEY
);

-- Currency Table
CREATE TABLE target.currency (
    currency_code VARCHAR(16) PRIMARY KEY
);

-- Transaction Status Table
CREATE TABLE target.tx_status (
    tx_status_code VARCHAR(16) PRIMARY KEY
);

-- Base Transaction Table
CREATE TABLE target.base_transaction (
    id SERIAL PRIMARY KEY,
    event_timestamp TIMESTAMP,
    user_id VARCHAR(32),
    amount FLOAT,
    currency_code VARCHAR(16),
    tx_status_code VARCHAR(16),
    type VARCHAR(16),
    FOREIGN KEY (user_id) REFERENCES target."user"(user_id),
    FOREIGN KEY (currency_code) REFERENCES target.currency(currency_code),
    FOREIGN KEY (tx_status_code) REFERENCES target.tx_status(tx_status_code)
);

-- Deposit Table (inherits from base_transaction)
CREATE TABLE target.deposit (
    CHECK (type = 'deposit')
) INHERITS (target.base_transaction);

-- Withdrawal Table (inherits from base_transaction)
CREATE TABLE target.withdrawal (
    interface VARCHAR(16),
    CHECK (type = 'withdrawal')
) INHERITS (target.base_transaction);

-- Base Event Table
CREATE TABLE target.base_event (
    id SERIAL PRIMARY KEY,
    event_timestamp TIMESTAMP,
    user_id VARCHAR(32),
    event_name VARCHAR(32),
    FOREIGN KEY (user_id) REFERENCES target."user"(user_id)
);

-- Login Event Table (inherits from base_event)
CREATE TABLE target.login_event (
    CHECK (event_name = 'login')
) INHERITS (target.base_event);

-- Event Table (inherits from base_event)
CREATE TABLE target.event (
) INHERITS (target.base_event);

