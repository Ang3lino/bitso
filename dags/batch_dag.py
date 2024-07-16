from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd

# Define the SQL queries to run
queries = {
    'query1': 'SELECT COUNT(DISTINCT user_id) AS active_users FROM (SELECT user_id FROM target.deposit WHERE DATE(event_timestamp) = \'2020-08-20\' UNION SELECT user_id FROM target.withdrawal WHERE DATE(event_timestamp) = \'2020-08-20\') AS active_users_on_date;',
    'query2': 'SELECT user_id FROM target."user" WHERE user_id NOT IN (SELECT DISTINCT user_id FROM target.deposit);',
    'query3': 'SELECT user_id, count(*) AS deposit_count FROM target.deposit GROUP BY user_id HAVING COUNT(*) > 5;',
    'query4': 'SELECT user_id, MAX(event_timestamp) AS last_login FROM target.login_event GROUP BY user_id;',
    'query5': 'SELECT user_id, COUNT(*) AS login_count FROM target.login_event WHERE event_timestamp BETWEEN \'2020-08-20\' AND \'2020-08-21\' GROUP BY user_id;',
    'query6': 'SELECT COUNT(DISTINCT currency_code) AS unique_currencies_deposited FROM target.deposit WHERE DATE(event_timestamp) = \'2020-08-20\';',
    'query7': 'SELECT COUNT(DISTINCT currency_code) AS unique_currencies_withdrew FROM target.withdrawal WHERE DATE(event_timestamp) = \'2020-08-20\';',
    'query8': 'SELECT SUM(amount) AS total_amount_deposited FROM target.deposit WHERE DATE(event_timestamp) = \'2020-08-20\' AND currency_code = \'mxn\';',
}

# Default arguments for the DAG
default_args = {
    'owner': 'angel',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 15),  # Adjust start date as needed
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Initialize the DAG
dag = DAG(
    'daily_batch',
    default_args=default_args,
    description='Daily ETL process',
    schedule_interval='@daily',
    template_searchpath=['/opt/airflow']
)

# PostgreSQL connection ID
POSTGRES_CONN_ID = 'postgres_default'

# Task to truncate data
truncate_data = PostgresOperator(
    task_id='truncate_data',
    postgres_conn_id=POSTGRES_CONN_ID,  # Modify connection ID as per your setup
    sql='sql/truncate.sql',
    dag=dag,
)

# Task to insert data (users, currencies, statuses, deposits, withdrawals, events, and login events)
insert_data = PostgresOperator(
    task_id='insert_data',
    postgres_conn_id=POSTGRES_CONN_ID,  # Modify connection ID as per your setup
    sql='sql/migration.sql',
    dag=dag,
)

# Define task dependencies
truncate_data >> insert_data

# Function to run a query and save the result to a CSV file
def run_query_and_save_to_csv(query_id, query, **kwargs):
    pg_hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    column_names = [desc[0] for desc in cursor.description]
    df = pd.DataFrame(data, columns=column_names)
    df.to_csv(f'/opt/airflow/bucket/batch_output/{query_id}.csv', index=False)
    cursor.close()
    conn.close()

# Create tasks for each query
for query_id, query in queries.items():
    task = PythonOperator(
        task_id=f'run_{query_id}',
        python_callable=run_query_and_save_to_csv,
        op_args=[query_id, query],
        dag=dag,
    )
    insert_data >> task
