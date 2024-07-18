from airflow import DAG
from airflow.operators.dummy import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.utils.dates import days_ago
from datetime import datetime, timedelta

import pytest
import pandas as pd
import logging
import os
import sys


# Add the project directory to the sys.path for importing the DAG and related functions
TEST_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.abspath(os.path.join(TEST_DIR, os.pardir))
sys.path.insert(0, PROJECT_DIR)


# Import the actual DAG and related functions from the DAG file
from dags.batch_dag import run_query_and_save_to_csv, dag as actual_dag, POSTGRES_CONN_ID


@pytest.fixture
def dag_fixture():
    """Fixture to provide the DAG object for tests."""
    return actual_dag

def test_dag_structure(dag_fixture):
    """Test to ensure the DAG has the correct structure and tasks."""
    # Print all task IDs to debug the task count issue
    task_ids = [task.task_id for task in dag_fixture.tasks]
    print(f"Tasks in the DAG: {task_ids}")

    # Assert the number of tasks
    assert len(dag_fixture.tasks) == 12

    # List of expected task IDs in the DAG
    expected_task_ids = [
        'start_task',
        'truncate_data',
        'insert_data',
        'end_task'
    ] + [f'run_query{i}' for i in range(1, 9)]

    # Ensure all expected tasks are present in the DAG
    for task_id in expected_task_ids:
        assert task_id in task_ids

def test_run_query_and_save_to_csv(mocker):
    """Test the run_query_and_save_to_csv function."""
    query_id = 'test_query'
    query = 'SELECT 1'

    # Call the function to run the query and save the result to a CSV file
    run_query_and_save_to_csv(query_id, query)

    # Verify that the output file exists
    output_file = f'/opt/airflow/bucket/batch_output/{query_id}.csv'
    assert os.path.exists(output_file)

    # Verify the contents of the output file
    df = pd.read_csv(output_file)
    assert len(df) == 1
    assert df.iloc[0, 0] == 1

def test_task_dependencies(dag_fixture):
    """Test the dependencies between tasks in the DAG."""
    # Get the tasks from the DAG
    truncate_data = dag_fixture.get_task('truncate_data')
    insert_data = dag_fixture.get_task('insert_data')

    # Verify upstream and downstream dependencies
    assert truncate_data.upstream_task_ids == {'start_task'}
    assert insert_data.upstream_task_ids == {'truncate_data'}

    for i in range(1, 9):
        query_task = dag_fixture.get_task(f'run_query{i}')
        assert query_task.upstream_task_ids == {'insert_data'}
        assert query_task.downstream_task_ids == {'end_task'}

def test_postgres_operator(dag_fixture):
    """Test the SQLExecuteQueryOperator with a simple query."""
    task = SQLExecuteQueryOperator(
        task_id='test_postgres',
        conn_id=POSTGRES_CONN_ID,
        sql='SELECT 1;',
        dag=dag_fixture
    )

    # Verify the task properties
    assert task.sql == 'SELECT 1;'
    assert task.conn_id == POSTGRES_CONN_ID
