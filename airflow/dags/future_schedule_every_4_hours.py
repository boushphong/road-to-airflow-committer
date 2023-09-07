from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta
from pendulum import today

dag = DAG(
    "future_schedule_every_4_hours",
    start_date=today() + timedelta(days=5),
    schedule=timedelta(hours=4),
    catchup=True,
)
task = EmptyOperator(task_id="empty_task", dag=dag)
