
from pyflink.table import EnvironmentSettings, TableEnvironment
from pyflink.table.expressions import *
from pyflink.table.table import Table
import os

##### t_env is a Table Environment - the entry point and central context for creating Table and SQL API programs
##### execute_sql() : Executes the given single statement, and return the execution result (status) -> OK or error.
##### Automatically REGISTERS the table 'restuarant_live_pending_orders' (maybe?)
##### from_path() : Reads a registered table and returns the resulting Table

def log_processing():

    env_settings = EnvironmentSettings.in_streaming_mode()
    t_env = TableEnvironment.create(env_settings)
    t_env.get_config().set("pipeline.jars", "file:///app/flink-sql-connector-kafka-1.17.1.jar;file:///app/mysql-connector-j-8.0.32.jar;file:///app/flink-connector-jdbc-3.1.0-1.17.jar")
    t_env.get_config().set("table.exec.source.idle-timeout", "1000")
    
    source_ddl = """
            CREATE TABLE restuarant_live_pending_orders(
                rest_id VARCHAR,
                status VARCHAR
            ) WITH (
              'connector' = 'kafka',
              'topic' = 'live_order_status',
              'properties.bootstrap.servers' = 'broker:29092',
              'properties.group.id' = 'rest_group',
              'scan.startup.mode' = 'specific-offsets',
              'scan.startup.specific-offsets' = 'partition:0,offset:0',
              'json.fail-on-missing-field' = 'false',
              'json.ignore-parse-errors' = 'true',
              'format' = 'json'
            )
            """
    t_env.execute_sql(source_ddl)
    # tbl = t_env.from_path('restuarant_live_pending_orders')
    # tbl.execute().print()
    
    # Get JDBC connection details from environment variables
    jdbc_url = os.environ.get('MYSQL_JDBC_URL')
    jdbc_table_name = os.environ.get('MYSQL_TABLE_NAME')
    jdbc_username = os.environ.get('MYSQL_USERNAME')
    jdbc_password = os.environ.get('MYSQL_PASSWORD')
    
    sink_mysql = f"""
        CREATE TABLE pending_orders_table (
        rest_id VARCHAR,
        pending_count INT,
        PRIMARY KEY (rest_id) NOT ENFORCED
    ) WITH (
        'connector' = 'jdbc',
        'url' = '{jdbc_url}',
        'table-name' = '{jdbc_table_name}',
        'username' = '{jdbc_username}',
        'password' = '{jdbc_password}'
    )
    """
    t_env.execute_sql(sink_mysql)
    

    query = """
            INSERT INTO pending_orders_table
            SELECT rest_id, SUM(CASE WHEN status = 'NEW' THEN 1 WHEN status = 'PROCESSED' THEN -1 ELSE 0 END) AS pending_count
            FROM restuarant_live_pending_orders
            GROUP BY rest_id
        """
    
    t_env.execute_sql(query).wait()

    
if __name__ == '__main__':
    log_processing()