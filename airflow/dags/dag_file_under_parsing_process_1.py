from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta
from pendulum import today

dag = DAG(
    "dag_file_under_parsing_process_no1",
    start_date=today() - timedelta(days=5),
    schedule="0 0 * * *",
    catchup=True,
)
task = EmptyOperator(task_id="empty_task", dag=dag)
