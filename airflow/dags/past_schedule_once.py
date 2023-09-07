from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta
from pendulum import today

dag = DAG(
    "past_schedule_once",
    start_date=today() + timedelta(days=-5),
    schedule="@once",
    catchup=True,
)
task = EmptyOperator(task_id="empty_task", dag=dag)
