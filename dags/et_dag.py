from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from spread_functions import fetch_ticker_data, compute_spread, save_to_partitioned_directory

import logging
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 14),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

saved_records = []

def trigger_fetch_and_compute(book):
    data = fetch_ticker_data(book)
    logging.info(f'Data fetched for book {book}')
    logging.info(data)
    if data and data['success']:
        spread_record = compute_spread(data['payload'])
        logging.info('Spread computed')
        logging.info(spread_record)
        saved_records.append(spread_record)
        logging.info(f'Amount of rows to be saved: {len(saved_records)}')
        logging.info(saved_records)


def trigger_save_and_flush(base_path):
    global saved_records
    logging.info(f'Rows to be saved: {len(saved_records)} in {os.getcwd()}')
    logging.info(os.listdir())
    if saved_records:
        save_to_partitioned_directory(saved_records, base_path)
        saved_records.clear()

BASE_PATH = "./bucket/get_ticker/"
BOOKS = ["btc_mxn", "usd_mxn"]

# DAG for fetching data every second
with DAG('fetch_spread_values',
         default_args=default_args,
         description='Fetch spread values every second',
         schedule_interval='* * * * *') as fetch_dag:

    for book in BOOKS:
        fetch_task = PythonOperator(
            task_id=f'fetch_and_compute_spread_{book}',
            python_callable=trigger_fetch_and_compute,
            op_args=[book],
            dag=fetch_dag
        )

# DAG for saving data every ten minutes
with DAG('save_spread_values',
         default_args=default_args,
         description='Save spread values every ten minutes',
         schedule_interval='*/10 * * * *') as save_dag:

    save_task = PythonOperator(
        task_id='save_and_flush_task',
        python_callable=trigger_save_and_flush,
        op_args=[BASE_PATH],
        dag=save_dag
    )
