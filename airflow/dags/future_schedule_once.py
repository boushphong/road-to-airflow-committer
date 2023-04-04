from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta; from pendulum import today
dag = DAG('future_schedule_once', start_date=today() + timedelta(minutes=2), schedule='@once', catchup=True)
task = EmptyOperator(task_id='empty_task',dag=dag)