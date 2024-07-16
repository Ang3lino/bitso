
-- 1. How many users were active on a given day (they made a deposit or withdrawal)
SELECT COUNT(DISTINCT user_id) AS active_users
FROM (
    SELECT user_id FROM target.deposit WHERE DATE(event_timestamp) = '2020-08-20'
    UNION
    SELECT user_id FROM target.withdrawal WHERE DATE(event_timestamp) = '2020-08-20'
) AS active_users_on_date;

-- 2. Identify users who haven't made a deposit
SELECT user_id
FROM target."user"
WHERE user_id NOT IN (
    SELECT DISTINCT user_id FROM target.deposit
);

-- 3. Identify on a given day which users have made more than 5 deposits historically
SELECT user_id, count(*) AS deposit_count
FROM target.deposit
GROUP BY user_id
HAVING COUNT(*) > 5
;

-- 4. When was the last time a user made a login
SELECT user_id, MAX(event_timestamp) AS last_login
FROM target.login_event
GROUP BY user_id;

-- 5. How many times a user has made a login between two dates
SELECT user_id, COUNT(*) AS login_count
FROM target.login_event
WHERE event_timestamp BETWEEN '2020-08-20' AND '2020-08-21'
GROUP BY user_id;

-- 6. Number of unique currencies deposited on a given day
SELECT COUNT(DISTINCT currency_code) AS unique_currencies_deposited
FROM target.deposit
WHERE DATE(event_timestamp) = '2020-08-20';

-- 7. Number of unique currencies withdrew on a given day
SELECT COUNT(DISTINCT currency_code) AS unique_currencies_withdrew
FROM target.withdrawal
WHERE DATE(event_timestamp) = '2020-08-20';

-- 8. Total amount deposited of a given currency on a given day
SELECT SUM(amount) AS total_amount_deposited
FROM target.deposit
WHERE DATE(event_timestamp) = '2020-08-20'
AND currency_code = 'mxn';

-- SELECT event_timestamp::date , SUM(amount) AS total_amount_deposited
-- FROM target.deposit
-- WHERE 
--   TRUE 
--   -- AND DATE(event_timestamp) = '2020-08-20'
--   AND currency_code = 'mxn'
-- GROUP BY 1
-- ORDER BY 2 DESC
-- ;

