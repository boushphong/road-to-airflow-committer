from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta
from pendulum import today

dag = DAG(
    "future_schedule_none",
    start_date=today() + timedelta(days=5),
    schedule=None,
    catchup=True,
)
task = EmptyOperator(task_id="empty_task", dag=dag)
