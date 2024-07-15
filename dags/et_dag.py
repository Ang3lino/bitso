
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from spread_functions import fetch_ticker_data, compute_spread, save_to_partitioned_directory

import logging
import requests
import os


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 14),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

URL_STORE_RECORD = "http://127.0.0.1:8000/store_spread"
URL_LOAD_SPREADS = 'http://127.0.0.1:8000/load_spreads'
HEADERS_JSON = { "Content-Type": "application/json" }


def trigger_fetch_and_compute(book: str) -> None:
    data = fetch_ticker_data(book)
    logging.info(f'Data fetched for book {book}')
    logging.info(data)
    if data and data['success']:  # if is not None and previous call was OK
        spread_record = compute_spread(data['payload'])
        logging.info('Spread computed')
        logging.info(spread_record)
        # call server save record
        response = requests.post(URL_STORE_RECORD, headers=HEADERS_JSON, json=spread_record)
        logging.info(f'Code response from endp {URL_STORE_RECORD} is {response}')

def trigger_save_and_flush():
    logging('Invoking method to save data from records')
    # call server save spreads
    response = requests.post(URL_LOAD_SPREADS, )
    logging.info(f'Code response from endp {URL_LOAD_SPREADS} is {response}')

BOOKS = ["btc_mxn", "usd_mxn"]

# DAG for fetching data every second
with DAG('fetch_spread_values',
         default_args=default_args,
         description='Fetch spread values every second',
        #  schedule_interval='* * * * *') as fetch_dag:
         schedule_interval='1 * * * *') as fetch_dag:
    for book in BOOKS:
        fetch_task = PythonOperator(
            task_id=f'fetch_and_compute_spread_{book}',
            python_callable=trigger_fetch_and_compute,
            op_args=[book],
            dag=fetch_dag
        )
        fetch_task

# DAG for saving data every ten minutes
with DAG('save_spread_values',
         default_args=default_args,
         description='Save spread values every ten minutes',
         schedule_interval='*/10 * * * *') as save_dag:
    save_task = PythonOperator(
        task_id='save_and_flush_task',
        python_callable=trigger_save_and_flush,
        # op_args=[BASE_PATH],
        dag=save_dag
    )
    save_task
