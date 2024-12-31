# Purpose of this file is to hold common environment/variable names
"""
API configurations
"""
CUSTOMER_DATA_ENDPOINT = "customerData"
LANDING_BUCKET = "t3-test-landing-zone"
LANDING_MOCKAROO_DIR = "mockaroo-landing"
LANDING_CUSTOMER_DATA_SUBDIR = "customer-data-v1"
LANDING_CUSTOMER_DATA_BLOB_ARCHETYPE = "response-cd-v1"

"""
GCP configurations
"""
GCP_SERVICE_ACCT = "saGCS"

"""
BQ configurations
"""
BQ_PROJECT_ID = "sandbox-data-pipelines"

BQ_DATASET_RAW = "raw_layer"
BQ_DATASET_CLEAN = "clean_layer"

BQ_TABLE_LANDING = "mockaroo_customer_data_landing_external"
BQ_TABLE_RAW = "mockaroo_customer_data_v1_historic"
