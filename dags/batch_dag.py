
from airflow import DAG
from airflow.operators.postgres_operator import PostgresOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'angel',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 15),  # Adjust start date as needed
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG(
    'daily_batch',
    default_args=default_args,
    description='Daily ETL process',
    schedule_interval='@daily',
    template_searchpath=['/opt/airflow']
    # template_seachpath=['/opt/airflow/sql']
)

# Task Insert users, currencies, statuses, deposits, withdrawals, events, and login events
insert_data = PostgresOperator(
    task_id='insert_data',
    postgres_conn_id='postgres_default',  # Modify connection ID as per your setup
    sql='sql/migration.sql',
    dag=dag,
)

insert_data