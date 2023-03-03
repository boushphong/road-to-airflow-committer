"""
A maintenance workflow that you can deploy into Airflow to periodically clean
out the DagRun, TaskInstance, Log, XCom, Job DB and SlaMiss entries to avoid
having too much data in your Airflow MetaStore.
airflow trigger_dag --conf '[curly-braces]"maxDBEntryAgeInDays":30[curly-braces]' airflow-db-cleanup
--conf options:
    maxDBEntryAgeInDays:<INT> - Optional
"""
import logging
import os
import pendulum
from datetime import timedelta
from typing import Type, Optional, List

import dateutil.parser
from airflow import settings
from airflow.jobs.base_job import BaseJob
from airflow.models import Base, DAG, DagTag, DagModel, DagRun, Log, TaskInstance, TaskReschedule, TaskFail
from airflow.operators.python import PythonOperator
from airflow.utils import timezone
from sqlalchemy import func, and_, Column
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import load_only
from sqlalchemy.sql.operators import ColumnOperators

NOW = timezone.utcnow
DAG_ID = os.path.basename(__file__).replace(".pyc", "").replace(".py", "")
START_DATE = pendulum.now().subtract(1)
SCHEDULE_INTERVAL = "@daily"
DAG_OWNER_NAME = "operations"
DEFAULT_MAX_DB_ENTRY_AGE_IN_DAYS = 3
ENABLE_DELETE = True
DATABASE_OBJECTS = []


def __deepcopy__(self, memo):
    memo[id(self)] = self
    return self


PythonOperator.__deepcopy__ = __deepcopy__


def add_database_object(
        airflow_db_model: Type[Base],
        age_check_column: Column,
        keep_last: bool = False,
        keep_last_filter: Optional[List[ColumnOperators]] = None,
        keep_last_group_by: Optional[Column] = None,
):
    DATABASE_OBJECTS.append(
        {
            "airflow_db_model": airflow_db_model,
            "age_check_column": age_check_column,
            "keep_last": keep_last,
            "keep_last_filter": keep_last_filter,
            "keep_last_group_by": keep_last_group_by,
        }
    )


add_database_object(BaseJob, BaseJob.latest_heartbeat)
add_database_object(DagRun, DagRun.execution_date)
add_database_object(TaskInstance, TaskInstance.start_date)
add_database_object(Log, Log.execution_date)
add_database_object(DagModel, DagModel.last_parsed_time)
add_database_object(TaskReschedule, TaskReschedule.start_date)
add_database_object(TaskFail, TaskFail.start_date)

session = settings.Session()

default_args = {
    "owner": DAG_OWNER_NAME,
    "depends_on_past": False,
    "start_date": START_DATE,
    "retries": 3,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG(
    DAG_ID,
    default_args=default_args,
    schedule=SCHEDULE_INTERVAL,
    start_date=START_DATE,
    tags=["airflow-maintenance-dags"],
)

if hasattr(dag, "doc_md"):
    dag.doc_md = __doc__
if hasattr(dag, "catchup"):
    dag.catchup = False


def print_configuration_function(**context) -> None:
    logging.info("Loading Configurations...")
    dag_run_conf = context.get("dag_run").conf
    logging.info(f"dag_run.conf: {str(dag_run_conf)}")
    max_db_entry_age_in_days = None
    if dag_run_conf:
        max_db_entry_age_in_days = dag_run_conf.get("maxDBEntryAgeInDays", None)
    logging.info(f"maxDBEntryAgeInDays from dag_run.conf: {str(dag_run_conf)}")
    if max_db_entry_age_in_days is None or max_db_entry_age_in_days < 1:
        logging.info(
            "maxDBEntryAgeInDays conf variable isn't included or Variable " +
            "value is less than 1. Using Default '" +
            str(DEFAULT_MAX_DB_ENTRY_AGE_IN_DAYS) + "'"
        )
        max_db_entry_age_in_days = DEFAULT_MAX_DB_ENTRY_AGE_IN_DAYS
    max_date = NOW() + timedelta(-max_db_entry_age_in_days)
    logging.info("Finished Loading Configurations\n")
    logging.info("Configurations:")
    logging.info(f"max_db_entry_age_in_days:    {str(max_db_entry_age_in_days)}")
    logging.info(f"max_date:                    {str(max_date)}")
    logging.info(f"enable_delete:               {str(ENABLE_DELETE)}")
    logging.info(f"session:                     {str(session)}")

    logging.info("Setting max_execution_date to XCom for Downstream Processes")
    context["ti"].xcom_push(key="max_date", value=max_date.isoformat())


def cleanup_function(**context) -> None:
    logging.info("Retrieving max_execution_date from XCom")
    max_date = context["ti"].xcom_pull(task_ids=print_configuration.task_id, key="max_date")
    max_date = dateutil.parser.parse(max_date)  # stored as iso8601 str in xcom

    airflow_db_model = context["params"].get("airflow_db_model")
    state = context["params"].get("state")
    age_check_column = context["params"].get("age_check_column")
    keep_last = context["params"].get("keep_last")
    keep_last_filters = context["params"].get("keep_last_filters")
    keep_last_group_by = context["params"].get("keep_last_group_by")

    logging.info("Configurations:")
    logging.info(f"max_date:            {str(max_date)}")
    logging.info(f"enable_delete:       {str(ENABLE_DELETE)}")
    logging.info(f"session:             {str(session)}")
    logging.info(f"airflow_db_model:    {str(airflow_db_model)}")
    logging.info(f"state:               {str(state)}")
    logging.info(f"age_check_column:    {str(age_check_column)}")
    logging.info(f"keep_last:           {str(keep_last)}")
    logging.info(f"keep_last_filters:   {str(keep_last_filters)}")
    logging.info(f"keep_last_group_by:  {str(keep_last_group_by)}")
    logging.info("Running Cleanup Process...")

    try:
        query = session.query(airflow_db_model).options(load_only(age_check_column))

        logging.info(f"INITIAL QUERY : {str(query)}")

        if keep_last:
            subquery = session.query(func.max(DagRun.execution_date))
            # workaround for MySQL "table specified twice" issue
            # https://github.com/teamclairvoyant/airflow-maintenance-dags/issues/41
            if keep_last_filters is not None:
                for entry in keep_last_filters:
                    subquery = subquery.filter(entry)

                logging.info(f"SUB QUERY [keep_last_filters]: {str(subquery)}")

            if keep_last_group_by is not None:
                subquery = subquery.group_by(keep_last_group_by)
                logging.info(f"SUB QUERY [keep_last_group_by]: {str(subquery)}")

            subquery = subquery.from_self()

            query = query.filter(and_(age_check_column.notin_(subquery)), and_(age_check_column <= max_date))

        else:
            query = query.filter(age_check_column <= max_date)

        entries_count = query.count()

        if ENABLE_DELETE:
            logging.info(f"Performing deletion of {entries_count} entries...")
            if airflow_db_model.__name__ == "DagModel":
                logging.info("Deleting tags...")
                ids_query = query.from_self().with_entities(DagModel.dag_id)
                tags_query = session.query(DagTag).filter(DagTag.dag_id.in_(ids_query))
                logging.info(f"Tags delete Query: {str(tags_query)}")
                tags_query.delete(synchronize_session=False)
            # using bulk delete
            query.delete(synchronize_session=False)
            session.commit()
            logging.info("Finished Performing Delete")
        else:
            logging.warning(
                f"You've opted to skip deleting {entries_count} entries. "
                f"Set ENABLE_DELETE to True to delete entries!!!"
            )

        logging.info("Finished Running Cleanup Process")

    except ProgrammingError as e:
        logging.error(e)
        logging.error(f"{str(airflow_db_model)} is not present in the metadata. Skipping...")


with dag:
    print_configuration = PythonOperator(
        task_id="print_configuration", python_callable=print_configuration_function, dag=dag
    )

    cleanup_tasks = [
        PythonOperator(
            task_id="cleanup_" + str(db_object["airflow_db_model"].__name__),
            python_callable=cleanup_function,
            params=db_object,
            dag=dag,
        )
        for db_object in DATABASE_OBJECTS
    ]
    print_configuration >> cleanup_tasks
