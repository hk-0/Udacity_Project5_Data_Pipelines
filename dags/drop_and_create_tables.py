import datetime
import logging
from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.postgres_operator import PostgresOperator



dag = DAG(
    'table_creation_dag',
    description='Drop and Create tables in Redshift using airflow',
    schedule_interval=None, #'0 * * * *',
    start_date=datetime.datetime(2022, 1, 1, 0, 0, 0, 0)
)
create_table_task = PostgresOperator(
    task_id="create_tables",
    dag=dag,
    postgres_conn_id="redshift",
    sql="create_tables.sql"
)
drop_table_task = PostgresOperator(
    task_id='drop_tables',
    dag=dag,
    postgres_conn_id="redshift",
    sql="drop_tables.sql"
)

drop_table_task >> create_table_task