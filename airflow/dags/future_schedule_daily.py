import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta; from pendulum import today
dag = DAG('future_schedule_daily', start_date=datetime.datetime(2030,1,1), schedule='0 0 * * *', catchup=True)
task = EmptyOperator(task_id='empty_task',dag=dag)