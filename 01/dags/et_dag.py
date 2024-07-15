
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from spread_functions import fetch_ticker_data, compute_spread, save_to_partitioned_directory
from tqdm import tqdm

import logging
import requests
import time
import os


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 14),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

BOOKS = ["btc_mxn", "usd_mxn"]
BASE_PATH = '/opt/airflow/bucket/get_ticker'


def trigger_fetch_and_compute(book: str, debug=True) -> None:
    data = fetch_ticker_data(book)
    if debug:
        logging.info(f'Data fetched for book {book}')
        logging.info(data)
    if data and data['success']:  # if is not None and previous call was OK
        spread_record = compute_spread(data['payload'])
        if debug:
            logging.info('Spread computed')
            logging.info(spread_record)
    return spread_record

def etl_spread(book: str) -> None:
    # start_time = time.time()
    # duration = 10 * 60  # 10 minutes in seconds
    duration = 1 * 60  # 1 minutes in seconds
    records = []
    # while time.time() - start_time < duration:
    for s in tqdm(range(duration)):
        record = trigger_fetch_and_compute(book, debug=False)
        time.sleep(1)  # Wait for 1 second
        records.append(record)
    logging.info(f'Writting records gathered from {duration} seconds.')
    save_to_partitioned_directory(records, BASE_PATH)


# DAG for saving data every ten minutes
with DAG('etl_ticker',
         default_args=default_args,
         description='Save spread values every ten minutes',
        #  schedule_interval='*/10 * * * *') as dag:
         schedule_interval='@daily') as dag:
    for book in BOOKS:
        fetch_task = PythonOperator(
            task_id=f'etl_{book}',
            python_callable=etl_spread,
            op_args=[book],
            dag=dag
        )
        fetch_task
