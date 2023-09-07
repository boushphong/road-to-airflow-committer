from airflow import DAG
import os
import logging
from datetime import datetime
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
import pendulum


def print_cwd():
    e = os.getenv("AIRFLOW_CONN_AIRFLOW_DB")
    logging.info(e)
    print(os.getcwd())


default_args = {"start_date": pendulum.today()}

with DAG(
    "print_cwd_scheduled_2",
    schedule="* * * * *",
    catchup=False,
    default_args=default_args,
) as dag:
    bash = BashOperator(task_id="bash_operator", bash_command="pwd")

    pwd = PythonOperator(
        task_id="print_current_working_directory", python_callable=print_cwd
    )

    sleep = BashOperator(task_id="sleep", bash_command="sleep 3")

    bash >> pwd >> sleep
