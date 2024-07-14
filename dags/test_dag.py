
from datetime import timedelta, datetime
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

import logging


default_args = {
    'owner': 'angel',
    'retries': 5, 
    'retry_delay': timedelta(minutes=1)
}

def greet():
    print('hello world')
    logging.info('log de informacion')
    print('uwu')


with DAG(
    default_args=default_args,
    dag_id='our_1st_dag',
    description='descripcion estetica',
    start_date=datetime(2024, 7, 13),
    schedule_interval='@daily'
) as dag:
    logging.info('esto se corre?')
    task1 = PythonOperator(
        task_id='greet',
        python_callable=greet
    )

    logging.info('esto no se imprime')
    task1
