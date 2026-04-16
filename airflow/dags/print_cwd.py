from __future__ import annotations

import logging
import os
from datetime import datetime, timezone

from airflow import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator


def _print_cwd():
    logging.info("AIRFLOW_CONN_AIRFLOW_DB=%s", os.getenv("AIRFLOW_CONN_AIRFLOW_DB"))
    logging.info("cwd=%s", os.getcwd())


with DAG(
    dag_id="print_cwd",
    schedule=None,
    start_date=datetime(2024, 1, 1, tzinfo=timezone.utc),
    catchup=False
) as dag:
    echo = BashOperator(
        task_id="echo",
        bash_command="echo 'hello from airflow 3' && pwd",
    )

    print_current_working_directory = PythonOperator(
        task_id="print_current_working_directory",
        python_callable=_print_cwd,
    )

    echo >> print_current_working_directory
