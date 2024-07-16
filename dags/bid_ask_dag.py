import logging
import os
import time
from datetime import datetime, timedelta

import requests
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from spread_functions import fetch_ticker_data, compute_spread, save_to_partitioned_directory
from tqdm import tqdm

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 7, 14),
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

BOOKS = ["btc_mxn", "usd_mxn"]
BASE_PATH = '/opt/airflow/bucket/get_ticker'

def trigger_fetch_and_compute(book: str, debug: bool = True) -> dict:
    """
    Fetch ticker data and compute the spread for a given book.
    
    Parameters:
        book (str): The book to fetch data for.
        debug (bool): Flag to enable debug logging.
        
    Returns:
        dict: The spread record.
    """
    data = fetch_ticker_data(book)
    if debug:
        logging.info(f'Data fetched for book {book}')
        logging.info(data)
    if data and data['success']:
        spread_record = compute_spread(data['payload'])
        if debug:
            logging.info('Spread computed')
            logging.info(spread_record)
        return spread_record
    return None

def etl_spread(book: str) -> None:
    """
    Perform ETL process to fetch and compute spread values for a given book.
    
    Parameters:
        book (str): The book to fetch data for.
    """
    duration = 10 * 60  # 10 minutes in seconds
    records = []
    
    for _ in tqdm(range(duration)):
        record = trigger_fetch_and_compute(book, debug=False)
        time.sleep(1)  # Wait for 1 second
        if record:
            records.append(record)
            # if record['spread'] > custom_value:  # in case exceed threshold we notify
            #     emit_alarm(record)
    
    logging.info(f'Writing records gathered from {duration} seconds.')
    save_to_partitioned_directory(records, BASE_PATH, book)

# Define the DAG for saving data every ten minutes
with DAG(
    'etl_ticker',
    default_args=default_args,
    description='Save spread values every ten minutes',
    schedule_interval='*/10 * * * *',
) as dag:
    for book in BOOKS:
        fetch_task = PythonOperator(
            task_id=f'etl_{book}',
            python_callable=etl_spread,
            op_args=[book],
            dag=dag
        )
        fetch_task
