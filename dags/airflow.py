from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from spread_functions import fetch_ticker_data, compute_spread, save_to_partitioned_directory

import os


print(os.listdir())
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 14),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

BASE_PATH = "./bucket/get_ticker/"
BOOKS = ["btc_mxn", "usd_mxn"]
saved_records = []

with DAG('save_spread_values',
         default_args=default_args,
         description='Fetch and save spread values every second, flush every ten minutes',
         schedule_interval='* * * * *') as dag:


    def trigger_fetch_and_compute(book):
        spread_record = compute_spread(fetch_ticker_data(book))
        saved_records.append(spread_record)

    for book in BOOKS:
        fetch_task = PythonOperator(
            task_id=f'fetch_and_compute_spread_{book}',
            python_callable=trigger_fetch_and_compute,
            op_args=[book],
        )

        fetch_task

    def trigger_save_and_flush():
        if saved_records:
            save_to_partitioned_directory(saved_records, BASE_PATH)
            saved_records.clear()

    save_task = PythonOperator(
        task_id='save_and_flush_task',
        python_callable=trigger_save_and_flush,
        dag=dag,
        # Schedule this task to run every ten minutes
        schedule_interval='*/10 * * * *',
    )

    fetch_task >> save_task
