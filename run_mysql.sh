docker stop some-mysql
docker rm some-mysql

docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=phong123 -e MYSQL_DATABASE=airflow_db -e MYSQL_USER=airflow -e MYSQL_ROOT_PASSWORD=phong123 -d -p 33066:3306 mysql:5.7

export AIRFLOW_HOME="$(pwd)/airflow"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="mysql+mysqlconnector://root:phong123@localhost:33066/airflow_db"
export AIRFLOW__DATABASE__SQL_ALCHEMY_SCHEMA="airflow_db"

# set global sql_mode = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';