from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
    COPY_SQL = """
        COPY {}
        FROM '{}'
        ACCESS_KEY_ID '{}'
        SECRET_ACCESS_KEY '{}'
        REGION '{}'
        JSON '{}'
    """

    @apply_defaults
    def __init__(self,
                 redshift_conn_id="",
                 aws_credentials_id = "",
                 table="",
                 s3_path="",
                 json_path="",
                 aws_region = "",
                 truncate = False,
                 *args, **kwargs):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_path = s3_path
        self.json_path = json_path
        self.aws_region = aws_region
        self.truncate = truncate
        self.execution_date = kwargs.get('execution_date')

    def execute(self, context):
        self.log.info('\n*** StageToRedshiftOperator: Copying data from S3 to Redshift ***')
        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()
        redshift_hook = PostgresHook(postgres_conn_id = self.redshift_conn_id)
        
        if self.truncate:
            self.log.info(f'Truncate Redshift table {self.table}')
            redshift_hook.run(f'TRUNCATE {self.table}')

        formatted_sql = StageToRedshiftOperator.COPY_SQL.format(
            self.table, self.s3_path, credentials.access_key, 
            credentials.secret_key, self.aws_region, self.json_path
        )
        
        #Run Data Load
        self.log.info(f'Copying data from {self.s3_path} to Redshift {self.table} table')
        redshift_hook.run(formatted_sql)

