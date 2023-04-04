docker stop some-mysql
docker rm some-mysql

docker run --name some-mysql -e MYSQL_ROOT_PASSWORD=phong123 -e MYSQL_DATABASE=airflow_db -e MYSQL_USER=airflow -e MYSQL_ROOT_PASSWORD=phong123 -d -p 3306:3306 mysql:8.0.32

export AIRFLOW_HOME="$(pwd)/airflow"
export AIRFLOW__DATABASE__SQL_ALCHEMY_CONN="mysql+mysqlconnector://root:phong123@localhost:3306/airflow_db"
export AIRFLOW__DATABASE__SQL_ALCHEMY_SCHEMA="airflow_db"

# set global sql_mode = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
mysql --user=root --password=phong123 --host=localhost --port=3306 -D airflow_db -e "set global sql_mode = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION'"
