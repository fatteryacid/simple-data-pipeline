# Simple Data Pipeline

## Project summary
This project contains an end-to-end data pipeline, following the lifecycle of data starting from an API call to ending in a cloud data warehouse.

## Purpose
The purpose of this project and repo is to demonstrate how to develop a simple data pipeline and explain why certain design decisions were made.

## High Level Design
![high-level-architecture](/images/simple-data-pipeline-flow.svg)

This data pipeline follows an ELT paradigm using Google Cloud Platform, written in an Airflow framework. Data flows from an API to a Google Cloud Storage (GCS) bucket, then finally loaded to a time-partitioned BigQuery (BQ) table.

## Design Decisions
### 1. ELT Paradigm
An ELT paradigm was chosen to avoid in-memory processing. 

If data was transformed in-memory, inside Airflow, it can bottleneck Airflow background services by competing for resources as the data scales. Alternatively, transformations can be ran in a serverless function such as Google Cloud Run Functions, however that adds another layer of complexity and pricing to balance.

Given the scope of this project, landing data in GCS and loading into BQ via external table can utilize BQ's compute engine for all processing instead of doing so in memory, while staying within the Free tier limits of both GCS and BQ. [[Source](https://cloud.google.com/bigquery/docs/external-tables#pricing)]

Some known tradeoffs are:
- GCS and BQ incur storage charges twice
- External query charges will scale with data

### 2. Time-Partitioned Raw Table
Raw table in BQ will serve as the master copy for the data warehouse.

This table contains all ingestions, partitioned by day so any downstream tables can be completely reconstructed in the event of a disaster.

In this design, GCS only serves as a temporary "landing" layer for data, meaning all GCS blobs will be expired/deleted within a timeframe.


## Setup
Although this program is a demo, `docker-compose.yaml` and `Dockerfile` are provided so you can set this up locally and play around with the code.

You will need to provide your own cloud profiles and API endpoints.

1. Clone this repository
2. Navigate to the directory this repository is cloned in
3. Run `docker compose build`. This will build the necessary docker images
4. Run `docker compose up -d`. This will start the docker containers "detached", which allows them to run in the background.
5. Navigate to `localhost:8080` on your browser to check Airflow.
