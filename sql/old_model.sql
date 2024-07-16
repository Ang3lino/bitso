

DROP TABLE IF EXISTS deposit;
DROP TABLE IF EXISTS event;
DROP TABLE IF EXISTS user_id;
DROP TABLE IF EXISTS withdrawals;

-- tables creation
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
    , event_name VARCHAR(32)
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

-- Efficient insert from csv
\COPY deposit
    FROM '/opt/airflow/bucket/samples/deposit_sample_data.csv'
    DELIMITER ','
    CSV HEADER;

\COPY event
    FROM '/opt/airflow/bucket/samples/event_sample_data.csv'
    DELIMITER ','
    CSV HEADER;

\COPY user_id
    FROM '/opt/airflow/bucket/samples/user_id_sample_data.csv'
    DELIMITER ','
    CSV HEADER;

\COPY withdrawals
    FROM '/opt/airflow/bucket/samples/withdrawals_sample_data.csv'
    DELIMITER ','
    CSV HEADER;

-- Validating proper ingestion
SELECT * FROM event LIMIT 10;
SELECT * FROM user_id LIMIT 10;
SELECT * FROM deposit LIMIT 10;
SELECT * FROM withdrawals LIMIT 10;
