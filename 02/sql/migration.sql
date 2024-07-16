
-- from source there was an empty record
delete from user_id where user_id is null;

-- Insert users from the old database to the new database
INSERT INTO target."user" (user_id)
SELECT DISTINCT user_id
FROM user_id;

-- Insert distinct currencies from deposits and withdrawals
INSERT INTO target.currency (currency_code)
SELECT DISTINCT currency
FROM deposit
UNION
SELECT DISTINCT currency
FROM withdrawals;

-- Insert distinct transaction statuses from deposits and withdrawals
INSERT INTO target.tx_status (tx_status_code)
SELECT DISTINCT tx_status
FROM deposit
UNION
SELECT DISTINCT tx_status
FROM withdrawals;

-- Insert deposits into the target deposit table
INSERT INTO target.deposit (event_timestamp, user_id, amount, currency_code, tx_status_code, type)
SELECT event_timestamp, user_id, amount, currency AS currency_code, tx_status AS tx_status_code, 'deposit' AS type
FROM deposit;

-- Insert withdrawals into the target withdrawal table
INSERT INTO target.withdrawal (event_timestamp, user_id, amount, currency_code, tx_status_code, interface, type)
SELECT event_timestamp, user_id, amount, currency AS currency_code, tx_status AS tx_status_code, interface, 'withdrawal' AS type
FROM withdrawals;

-- Insert events into the target event table
INSERT INTO target.event (event_timestamp, user_id, event_name)
SELECT event_timestamp, user_id, event_name
FROM event;

-- Insert login events into the target login_event table
INSERT INTO target.login_event (event_timestamp, user_id, event_name)
SELECT event_timestamp, user_id, event_name
FROM event
WHERE event_name = 'login';

