from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import timedelta; from pendulum import today
dag = DAG('future_schedule_daily', start_date=today() + timedelta(days=5), schedule='0 0 * * *', catchup=True)
task = EmptyOperator(task_id='empty_task',dag=dag)