from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'post_spread_data',
    default_args=default_args,
    description='DAG to POST spread data to a given endpoint',
    schedule_interval=timedelta(days=1),
    start_date=days_ago(1),
    tags=['example'],
) as dag:

    post_spread_task = SimpleHttpOperator(
        task_id='post_spread_task',
        http_conn_id='http_default',  # Connection ID configured in Airflow
        endpoint='store_spread',
        method='POST',
        headers={"Content-Type": "application/json"},
        data='''{
            "orderbook_timestamp": "2024-07-14T12:00:00+00:00",
            "book": "btc_mxn",
            "bid": 790000.00,
            "ask": 800000.00,
            "spread": 1.10
        }''',
        response_check=lambda response: response.status_code == 200,
        log_response=True,
    )

    post_spread_task
