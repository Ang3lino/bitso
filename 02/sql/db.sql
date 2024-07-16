
-- db apart from airflow
CREATE DATABASE batch;

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

-- Inspecting
select event_timestamp from withdrawals order by 1 desc limit 10;
select distinct extract(day from event_timestamp) from withdrawals order by 1 desc limit 10;
select min(extract(day from event_timestamp))
  , max(extract(day from event_timestamp))
  from withdrawals;

select min(event_timestamp) , max(event_timestamp) from withdrawals;
select distinct event_timestamp::date from withdrawals order by 1 desc limit 10;

SELECT event_timestamp::date as mdate, COUNT(distinct user_id) as mcount
    FROM withdrawals
  group by mdate 
  order by mcount desc
  limit 10
;

   mdate    | mcount
------------+--------
 2020-08-20 |     15
 2020-10-22 |     11
 2021-03-10 |      9
 2021-04-20 |      9
 2021-04-21 |      8
 2020-04-30 |      8
 2020-09-22 |      8
 2020-05-22 |      8
 2020-12-08 |      7
 2020-12-10 |      7
(10 rows)

SELECT event_timestamp::date as mdate, COUNT(distinct user_id) as mcount
    FROM deposit
  group by mdate 
  order by mcount desc
  limit 10
;

   mdate    | mcount
------------+--------
 2021-02-19 |   8834
 2022-05-20 |   4984
 2022-05-17 |    462
 2022-06-21 |    286
 2022-05-23 |    203
 2022-05-25 |     73
 2022-06-23 |     44
 2022-06-24 |     44
 2022-06-27 |     43
 2022-06-09 |     42
(10 rows)

