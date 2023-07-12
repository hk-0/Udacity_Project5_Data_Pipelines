from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadDimensionOperator(BaseOperator):

    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id = "",
                 target_db = "",
                 destination_table = "",
                 sql = "",
                 truncate = True,
                 *args, **kwargs):

        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.target_db = target_db
        self.destination_table = destination_table
        self.sql = sql
        self.truncate = truncate
        
    def execute(self, context):
        self.log.info('\n*** LoadDimensionOperator: Inserting data into Dimension tables ***')
        redshift_hook = PostgresHook(postgres_conn_id = self.redshift_conn_id)
        insert_sql = f'INSERT INTO {self.destination_table} ({self.sql})'

        if self.truncate:
            self.log.info(f'\n*** Truncating table {self.destination_table} ***')
            redshift_hook.run(f'TRUNCATE TABLE {self.destination_table}')

        self.log.info(f'\n*** Loading data into {self.target_db}.{self.destination_table} ***')
        self.log.info(f"Running SQL: {insert_sql}")
        
        redshift_hook.run(insert_sql)

        self.log.info(f"\n*** LoadDimensionOperator: Inserting data into Dimension tables Completed ***")