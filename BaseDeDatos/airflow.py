from airflow import DAG
from airflow.providers.google.cloud.sensors.gcs import GCSObjectUpdateSensor
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.dates import days_ago

default_args = {
    'start_date': days_ago(1),
    'retries': 1,
}

with DAG(
    'update_bigquery_on_file_update',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:

    # Sensor to wait for a file update
    file_updated = GCSObjectUpdateSensor(
        task_id='file_updated_sensor',
        bucket='adsac',
        object='Yelp/checkin.json',
        timeout=600,  # Timeout after 10 minutes
        poke_interval=30,  # Check every 30 seconds
    )

    # Update BigQuery table
    update_bigquery = BigQueryInsertJobOperator(
        task_id='update_bigquery',
        configuration={
            "query": {
                "query": """
                    MERGE `adsac-455509.Staging.CheckIn` T
                    USING `adsac-455509.Staging.CheckIn` S
                    ON T.id = S.id
                    WHEN MATCHED THEN
                      UPDATE SET T.column = S.column
                    WHEN NOT MATCHED THEN
                      INSERT ROW;
                """,
                "useLegacySql": False,
            }
        },
    )

    file_updated >> update_bigquery