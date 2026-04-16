docker stop some-postgres
docker rm some-postgres

docker run --name some-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=airflow_db -p 5432:5432 -d postgres

export AIRFLOW_HOME="$(pwd)/airflow"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://postgres:postgres@localhost:5432/airflow_db"
export AIRFLOW__DATABASE__SQL_ALCHEMY_SCHEMA="public"

sleep 4

airflow db migrate

echo "Jetbrains Environments"
echo "AIRFLOW_HOME=$AIRFLOW_HOME;AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=$AIRFLOW__DATABASE__SQL_ALCHEMY_CONN;AIRFLOW__DATABASE__SQL_ALCHEMY_SCHEMA=$AIRFLOW__DATABASE__SQL_ALCHEMY_SCHEMA"
