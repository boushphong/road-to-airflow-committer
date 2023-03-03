docker run --name some-postgres -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=airflow_db -p 5432:5432 -d postgres

export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/airflow_db"
export AIRFLOW__DATABASE__SQL_ALCHEMY_SCHEMA="public"

airflow db init