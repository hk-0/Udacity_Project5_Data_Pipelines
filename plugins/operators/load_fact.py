from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class LoadFactOperator(BaseOperator):

    ui_color = '#F98866'

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 # Example:
                 # conn_id = your-connection-name
                 redshift_conn_id = "",
                 target_db = "",
                 destination_table = "",
                 sql = "",
                 *args, **kwargs):

        super(LoadFactOperator, self).__init__(*args, **kwargs)
        # Map params here
        # Example:
        # self.conn_id = conn_id
        self.redshift_conn_id = redshift_conn_id
        self.target_db = target_db
        self.destination_table = destination_table
        self.sql = sql

    def execute(self, context):
        self.log.info('\n*** LoadFactOperator: Inserting data into Fact tables ***')
        redshift_hook = PostgresHook(postgres_conn_id = self.redshift_conn_id)
        insert_sql = f'INSERT INTO {self.destination_table} ({self.sql})'
        
        self.log.info(f'\n*** Loading data into {self.target_db}.{self.destination_table} ***')
        self.log.info(f"Running SQL: {insert_sql}")
        
        redshift_hook.run(insert_sql)

        self.log.info(f"\n*** LoadFactOperator: Inserting data into Fact tables Completed ***")