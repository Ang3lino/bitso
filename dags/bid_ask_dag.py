import logging
import time
import os
import requests

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy import DummyOperator
from datetime import datetime, timedelta
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

# SPREAD_THRESHOLD = 0.15
SPREAD_THRESHOLD = 0.1
BOOKS = ["btc_mxn", "usd_mxn"]
BASE_PATH = '/opt/airflow/bucket/get_ticker'
WEBHOOK_URL = "https://hooks.slack.com/services/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"

def emit_alarm(record: dict):
    """
    Sends an alarm (notification) using a webhook if a specific condition is met.
    
    Parameters:
        record (dict): The record that triggered the alarm.
    """
    try:
        message = {
            "text": f"Alert! Spread exceeded threshold: {record}",
        }
        response = requests.post(WEBHOOK_URL, json=message)
        if response.status_code != 200:
            logging.error(
                f"Request to webhook returned an error {response.status_code}, the response is: {response.text}"
            )
    except Exception as e:
        logging.error(f"Error sending alarm: {str(e)}")

def trigger_fetch_and_compute(book: str, debug: bool = True) -> dict:
    """
    Fetch ticker data and compute the spread for a given book.
    
    Parameters:
        book (str): The book to fetch data for.
        debug (bool): Flag to enable debug logging.
        
    Returns:
        dict: The spread record.
    """
    try:
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
    except Exception as e:
        logging.error(f"Error fetching and computing spread for book {book}: {str(e)}")
    return None

def etl_spread(book: str) -> None:
    """
    Perform ETL process to fetch and compute spread values for a given book.
    
    Parameters:
        book (str): The book to fetch data for.
    """
    try:
        duration = 10 * 60  # 10 minutes in seconds
        records = []

        for _ in tqdm(range(duration)):
            record = trigger_fetch_and_compute(book, debug=False)
            time.sleep(1)  # Wait for 1 second
            if record:
                records.append(record)
                if record['spread'] > SPREAD_THRESHOLD:  # in case exceed threshold we notify
                    logging.info(f"Threshold! {record}")
                    # SlackWebhookHook(webhook_token=WEBHOOK_URL, message=f"Alert! bid-ask has appeared {record}").execute()
                    emit_alarm(record)
        
        logging.info(f'Writing records gathered from {duration} seconds.')
        save_to_partitioned_directory(records, BASE_PATH, book)
    except Exception as e:
        logging.error(f"Error in ETL process for book {book}: {str(e)}")

# Define the DAG for saving data every ten minutes
with DAG(
    'etl_ticker',
    default_args=default_args,
    description='Save spread values every ten minutes',
    schedule_interval='*/10 * * * *',
) as dag:
    
    start_task = DummyOperator(task_id='start_task', dag=dag)
    end_task = DummyOperator(task_id='end_task', dag=dag)

    extract_transform_tasks = [
        PythonOperator(
            task_id=f'etl_{book}',
            python_callable=etl_spread,
            op_args=[book],
            dag=dag
        )
        for book in BOOKS
    ]

    start_task >> extract_transform_tasks >> end_task
