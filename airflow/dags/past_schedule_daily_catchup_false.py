from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta
from pendulum import today

dag = DAG(
    "past_schedule_daily_catchup_false",
    start_date=today() + timedelta(days=-5),
    schedule="0 0 * * *",
    catchup=False,
)
task = EmptyOperator(task_id="empty_task", dag=dag)
