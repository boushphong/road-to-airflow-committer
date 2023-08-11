rm $(pwd)/airflow/airflow-webserver.pid
pkill -f "airflow executor"
pkill -f "airflow worker"
pkill -f "airflow scheduler"
pkill -f "airflow webserver"