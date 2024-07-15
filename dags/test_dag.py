
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

import logging
import requests


default_args = {
    'owner': 'angel',
    'retries': 5, 
    'retry_delay': timedelta(minutes=1)
}

def greet():
    logging.info("fun started")
    # url = "http://127.0.0.1:8000/store_spread"
    url = "http://0.0.0.0:8000/store_spread"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "orderbook_timestamp": "2024-07-14T12:00:00+00:00",
        "book": "btc_mxn",
        "bid": 790000.00,
        "ask": 800000.00,
        "spread": 1.10
    }
    response = requests.post(url, headers=headers, json=data)
    print(response)


with DAG(
    default_args=default_args,
    dag_id='our_1st_dag',
    description='descripcion estetica',
    start_date=datetime(2024, 7, 13),
    schedule_interval='@daily'
) as dag:
    task1 = PythonOperator(
        task_id='greet',
        python_callable=greet
    )
    task1
