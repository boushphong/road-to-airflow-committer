docker stop some-postgres
docker rm some-postgres

docker run --name some-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=airflow_db -p 5432:5432 -d postgres

export AIRFLOW_HOME="$(pwd)/airflow"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_db"
export AIRFLOW__DATABASE__SQL_ALCHEMY_SCHEMA="public"

sleep 5

airflow db init

airflow users create -u admin -p admin -r Admin -e admin@admin.com -f Phong -l Bui

echo $AIRFLOW_HOME
echo $AIRFLOW__DATABASE__SQL_ALCHEMY_CONN
echo $AIRFLOW__DATABASE__SQL_ALCHEMY_SCHEMA
