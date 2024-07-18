
\COPY deposit FROM '/opt/airflow/bucket/samples/deposit_sample_data.csv' DELIMITER ',' CSV HEADER;
\COPY event FROM '/opt/airflow/bucket/samples/event_sample_data.csv' DELIMITER ',' CSV HEADER;
\COPY user_id FROM '/opt/airflow/bucket/samples/user_id_sample_data.csv' DELIMITER ',' CSV HEADER;
\COPY withdrawals FROM '/opt/airflow/bucket/samples/withdrawals_sample_data.csv' DELIMITER ',' CSV HEADER;