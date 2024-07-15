
-- db postgres

CREATE TABLE deposit (
    id INTEGER
    , event_timestamp TIMESTAMP
    , user_id VARCHAR(32)
    , amount FLOAT
    , currency VARCHAR(16)
    , tx_status VARCHAR(16)
);

CREATE TABLE event (
    id INTEGER
    , event_timestamp TIMESTAMP
    , user_id VARCHAR(32)
    , event_name VARCHAR(16)
);

CREATE TABLE user_id (
    user_id VARCHAR(32)
);

CREATE TABLE withdrawals (
      id INTEGER
    , event_timestamp TIMESTAMP
    , user_id VARCHAR(32)
    , amount FLOAT
    , interface VARCHAR(16)
    , currency VARCHAR(16)
    , tx_status VARCHAR(16)   
);
