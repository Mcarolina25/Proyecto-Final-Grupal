from airflow import DAG
from airflow.providers.http.operators.http import SimpleHttpOperator
from airflow.utils.dates import days_ago

default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'call_fastapi_example',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    call_fastapi = SimpleHttpOperator(
        task_id='call_fastapi',
        http_conn_id='fastapi_connection',  # Define this in Airflow connections
        endpoint='/your-endpoint',
        method='POST',
        data={"key": "value"},  # Payload for the API
        headers={"Content-Type": "application/json"},
    )
