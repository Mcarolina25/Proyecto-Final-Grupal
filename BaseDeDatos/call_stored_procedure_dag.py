from airflow import DAG
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago

# Default arguments for the DAG
default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

# Define the DAG
with DAG(
    'call_stored_procedure_dag',
    default_args=default_args,
    schedule_interval=None,  # Trigger manually
    catchup=False,
) as dag:

    # Task: Call the stored procedure
    call_stored_procedure = BigQueryInsertJobOperator(
        task_id='call_stored_procedure',
        configuration={
            "query": {
                "query": "CALL `adsac-455509.Curated.InsertCuratedData`();",
                "useLegacySql": False,
            }
        },
    )