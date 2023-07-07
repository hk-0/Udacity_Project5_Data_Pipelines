from datetime import datetime, timedelta
import os
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators import (StageToRedshiftOperator, LoadFactOperator,
                                LoadDimensionOperator, DataQualityOperator)
from helpers import SqlQueries

# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')

default_args = {
    'owner': 'udacity',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2019, 1, 12),
    'email_on_retry': False,
    'catchup': False
}

dag = DAG('sparkify_dag',
          default_args=default_args,
          description='Load and transform data in Redshift with Airflow',
          schedule_interval='0 * * * *'
        )

start_operator = DummyOperator(task_id='Begin_execution',  dag=dag)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id = 'redshift',
    aws_credentials_id = 'aws_credentials',
    table = "public.staging_events",
    s3_path = 's3://udacity-dend/log_data',
    json_path = 's3://udacity-dend/log_json_path.json',
    aws_region= 'us-west-2',
    truncate = False
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id = 'redshift',
    aws_credentials_id = 'aws_credentials',
    table = "public.staging_songs",
    s3_path = 's3://udacity-dend/song_data',
    json_path = 'auto',
    aws_region= 'us-west-2',
    truncate = False

)

load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    target_db = 'dev',
    destination_table = 'public.songplays',
    sql = SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    target_db = 'dev',
    destination_table = 'public.users',
    sql = SqlQueries.user_table_insert,
    truncate = True
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    target_db = 'dev',
    destination_table = 'public.songs',
    sql = SqlQueries.song_table_insert,
    truncate = True
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id = 'redshift',
    target_db = 'dev',
    destination_table = 'public.artists',
    sql = SqlQueries.artist_table_insert,
    truncate = True
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag, 
    redshift_conn_id = 'redshift',
    target_db = 'dev',
    destination_table = 'public.time',
    sql = SqlQueries.time_table_insert,
    truncate = True
)

run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id = 'redshift',
    tables = ["public.staging_events",
              "public.staging_songs",
              "public.songplays",
              "public.users",
              "public.songs",
              "public.artists",
              "public.time"
              ]
)

end_operator = DummyOperator(task_id='Stop_execution',  dag=dag)


start_operator >> (stage_events_to_redshift,stage_songs_to_redshift) >> load_songplays_table
load_songplays_table >> (load_song_dimension_table,
                         load_user_dimension_table,
                         load_artist_dimension_table,
                         load_time_dimension_table
                         ) >> run_quality_checks >> end_operator
