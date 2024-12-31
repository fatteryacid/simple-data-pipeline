from datetime import datetime
from google.cloud import storage
import json
import os
import requests

"""
General structure of this is:
1. DAG passes through authentication and timestamp arguments
2. workflows function handles API call & GCS write

TODO: Ensure these raise errors correctly when failing
TODO: Double check these functions for maintainability
"""
# def generate_blob_name(name_archetype, datetime_string):
#     return name_archetype + '-' + datetime_string

def generate_blob_name(bucket_directory, bucket_subdirectory, bucket_filename_archetype, timestamp):
    """
    Generates the path to the blob in GCS.
    """
    return '/'.join([bucket_directory, bucket_subdirectory, bucket_filename_archetype]) + timestamp

def make_get_request(url, params=None, headers=None):
    """
    Makes a get request to a specified endpoint and returns the response object IF status code is 200
    """
    response = requests.get(url=url, params=params, headers=headers)
    return json.dumps(response.json())

def convert_to_newline_delim_json(json_object):
    """
    Since BQ only takes JSONs that are newline delim, we need to convert all standard json strings
    """
    json_string = [json.dumps(record) for record in json.loads(json_object)]
    return '\n'.join(json_string)

def write_to_gcs(blob_name, file, bucket_name, creds):
    """
    Takes a file in memory and writes it as a blob to specified GCS bucket path
    """
    storage_client = storage.Client(credentials=creds)

    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_string(file)

def extract_from_api_to_gcs(url, blob_name, bucket_name, creds):
    """
    Runs above functions together in proper order
    """
    response = make_get_request(url=url)
    response = convert_to_newline_delim_json(response)
    write_to_gcs(blob_name, response, bucket_name, creds)
