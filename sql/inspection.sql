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
