from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.providers.google.common.hooks.base_google import GoogleBaseHook

from datetime import datetime
from pathlib import Path
import json

import os
import sys
sys.path.append("/opt/airflow/utils") # handles all python operations

import common
import services



DEFAULT_ARGS = {
    "start_date": datetime(2024, 12, 23),
}
DAG_ID = Path(__file__).name
CGS_SA = GoogleBaseHook(gcp_conn_id = common.GCP_SERVICE_ACCT).get_credentials()   # Use this airflow-google package to pass SA creds to python callable
BLOB_NAME = services.generate_blob_name(
    bucket_directory = common.LANDING_MOCKAROO_DIR,
    bucket_subdirectory = common.LANDING_CUSTOMER_DATA_SUBDIR,
    bucket_filename_archetype = common.LANDING_CUSTOMER_DATA_BLOB_ARCHETYPE,
    timestamp = "{{ ds }}"
)
CUR_DIR = os.path.abspath(os.path.dirname(__file__))

with DAG(dag_id=DAG_ID, default_args=DEFAULT_ARGS, catchup=False, schedule_interval="@hourly") as dag:

    extract_from_api_to_gcs = PythonOperator(
        # Local functions in ../utils/services.py
        # Handles API call -> GCS landing

        task_id = "extract_from_api_to_gcs",
        python_callable = services.extract_from_api_to_gcs,
        op_kwargs = { # these are the arguments specific to our extract function in ../utils/services.py
            "url": f"{{{{ var.value.{common.CUSTOMER_DATA_ENDPOINT} }}}}",
            "blob_name": BLOB_NAME,
            "bucket_name": common.LANDING_BUCKET,
            "creds": CGS_SA,
        }
    )

    load_from_gcs_to_bq = GCSToBigQueryOperator(
        # Loads raw GCS content via external table
        # - done to not incur any transfer costs
        # - external table treated as a staging table and will be removed

        task_id = "load_from_gcs_to_bq",
        bucket = common.LANDING_BUCKET,
        source_objects = [BLOB_NAME],
        destination_project_dataset_table = '.'.join([common.BQ_PROJECT_ID, common.BQ_DATASET_RAW, common.BQ_TABLE_LANDING]),
        source_format = "NEWLINE_DELIMITED_JSON",
        create_disposition = "CREATE_IF_NEEDED",
        external_table = True,
        autodetect = True,
        gcp_conn_id = common.GCP_SERVICE_ACCT,
    )

    load_from_raw_to_historic_raw_bq = BigQueryInsertJobOperator(
        # Loads raw GCS data -> historical time partitioned physical table in BQ
        # This is the true 'raw' layer in BQ

        # NOTE: this operator works on the partition level, meaning you will need to specify which partitions to modify
        # when you apply a write disposition, you it affects the partition itself

        task_id = "load_from_raw_bq_external_to_raw_bq_historic",
        gcp_conn_id = common.GCP_SERVICE_ACCT,
        configuration = {
            "query": {
                "query": open(f"{CUR_DIR}/workflows/customer_data_historic_load.sql", 'r').read(), #this is broken and i dont know why
                "useLegacySql": False,
                "priority": "BATCH",
                "writeDisposition": "WRITE_TRUNCATE",
                "destinationTable": {
                    "projectId": common.BQ_PROJECT_ID,
                    "datasetId": common.BQ_DATASET_RAW,
                    "tableId": common.BQ_TABLE_RAW + '$' + "{{ ds_nodash }}", # specifies partition to modify
                    "timePartitioning": {
                        "field": "execution_ts",
                        "type": "DAY"
                    },
                },
                "allow_large_results": True,
            }
        }
    )

    extract_from_api_to_gcs >> load_from_gcs_to_bq >> load_from_raw_to_historic_raw_bq
