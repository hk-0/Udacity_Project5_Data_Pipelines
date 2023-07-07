# Project Sparkify - Data Pipelines

## Introduction

A music streaming startup, Sparkify, has grown their user base and song database even more and want to move their data warehouse to a data lake. Their data resides in S3, in a directory of JSON logs on user activity on the app, as well as a directory with JSON metadata on the songs in their app.

As their data engineer, I am tasked with creating high grade data pipelines that are dynamic and built from reusable tasks, can be monitored, and allow easy backfills. They have also noted that the data quality plays a big part when analyses are executed on top the data warehouse and want to run tests against their datasets after the ETL steps have been executed to catch any discrepancies in the datasets.

## Project Description

In this project, I will apply what I've learned about the core concepts of Apache Airflow. To complete the project, I will need to create my own custom operators to perform tasks such as staging the data, filling the data warehouse, and running checks on the data as the final step.

## Database Model and Schema

The data model is implemented using a star schema. The schema contains two staging tables,`staging_events` and `staging_songs`, one fact table, `songplays`, and four dimension tables: `songs`, `artists`, `users` and `time`.

#### Staging Tables

**`staging_events`**
| COLUMN         | TYPE                 |
|----------------|----------------------|
| event_id       | BIGINT IDENTITY(1,1) |
| artist         | varchar              |
| auth           | varchar              |
| firstName      | varchar              |
| gender         | varchar              |
| itemInSession  | varchar              |
| lastName       | varchar              |
| length         | varchar              |
| level          | varchar              |
| location       | varchar              |
| method         | varchar              |
| page           | varchar              |
| registration   | varchar              |
| sessionId      | integer              |
| song           | varchar              |
| status         | integer              |
| ts             | bigint               |
| userAgent      | varchar              |
| userId         | integer              |

**`staging_songs`**
| COLUMN           | TYPE       |
|------------------|------------|
| num_songs        | integer    |
| artist_id        | varchar    |
| artist_latitude  | varchar    |
| artist_longitude | varchar    |
| artist_location  | varchar    |
| artist_name      | varchar    |
| song_id          | varchar    |
| title            | varchar    |
| duration         | decimal(9) |
| year             | integer    |


#### Fact Tables

**`songplays`**
| COLUMN      | TYPE      | CONSTRAINT  |
|-------------|-----------|-------------|
| songplay_id | SERIAL    | PRIMARY KEY |
| start_time  | TIMESTAMP | NOT NULL    |
| user_id     | INT       | NOT NULL    |
| level       | VARCHAR   |             |
| song_id     | VARCHAR   |             |
| artist_id   | VARCHAR   |             |
| session_id  | INT       |             |
| location    | VARCHAR   |             |
| user_agent  | VARCHAR   |             |

#### Dimension Tables

**`users`**
| COLUMN     | TYPE    | CONSTRAINT  |
|------------|---------|-------------|
| user_id    | INT     | PRIMARY KEY |
| first_name | VARCHAR | NOT NULL    |
| last_name  | VARCHAR | NOT NULL    |
| gender     | VARCHAR |             |
| level      | VARCHAR |             |

**`songs`**
| COLUMN    | TYPE    | CONSTRAINT  |
|-----------|---------|-------------|
| song_id   | VARCHAR | PRIMARY KEY |
| title     | VARCHAR | NOT NULL    |
| artist_id | VARCHAR | NOT NULL    |
| year      | INT     | NOT NULL    |
| duration  | NUMERIC | NOT NULL    |

**`artist`**
| COLUMN    | TYPE             | CONSTRAINT  |
|-----------|------------------|-------------|
| artist_id | VARCHAR          | PRIMARY KEY |
| name      | VARCHAR          | NOT NULL    |
| location  | VARCHAR          |             |
| latitude  | DOUBLE PRECISION |             |
| longitude | DOUBLE PRECISION |             |

**`time`**
| COLUMN     | TYPE      | CONSTRAINT  |
|------------|-----------|-------------|
| start_time | TIMESTAMP | PRIMARY KEY |
| hour       | INT       |             |
| day        | INT       |             |
| week       | INT       |             |
| month      | INT       |             |
| year       | INT       |             |
| weekday    | INT       |             |

## File Structure And Description

```
.
└── airflow
    ├── dags
    │   ├── create_tables.sql (Contains sql statements to create the required tables in redshift)
    │   ├── drop_and_create_tables.py (Defines that tasks to drop and recreates the tables in redshift)
    │   ├── drop_tables.sql (Contains sql statements that drops the tables in redshift)
    │   └── sparkify_dag.py (Defines the tasks and their order of execution for the data pipeline)
    ├── plugins
    │   ├── helpers
    │   │   ├── __init__.py
    │   │   └── sql_queries.py (Contains the sql statements to transform data from staging tables into the fact and dimension tables)
    │   ├── __init__.py
    │   ├── operators
    │   │   ├── __init__.py
    │   │   ├── data_quality.py (Custom operator used to run checks on the data itself)
    │   │   ├── load_dimension.py (Custom operator used to load the dimension tables)
    │   │   ├── load_fact.py (Custom operator used to load the fact tables)
    │   │   └── stage_redshift.py (Custom operator used to load JSON data residing on S3 into the staging tables using COPY command)
    └── README.md

```
## Project Dataset

S3 data path

- Song data: `s3://udacity-dend/song_data`
- Log data: `s3://udacity-dend/log_data`


### Song Dataset

The first dataset is a subset of real data from the Million Song Dataset. Each file is in JSON format and contains metadata about a song and the artist of that song. The files are partitioned by the first three letters of each song's track ID. For example, here are filepaths to two files in this dataset.

`song_data/A/B/C/TRABCEI128F424C983.json`

`song_data/A/A/B/TRAABJL12903CDCF1A.json`

And below is an example of what a single song file, `TRAABJL12903CDCF1A.json`, looks like.

> {"num_songs": 1, "artist_id": "ARJIE2Y1187B994AB7", "artist_latitude": null, "artist_longitude": null, "artist_location": "", "artist_name": "Line Renaud", "song_id": "SOUPIRU12A6D4FA1E1", "title": "Der Kleine Dompfaff", "duration": 152.92036, "year": 0}

### Log Dataset

The second dataset consists of log files in JSON format generated by this event simulator based on the songs in the dataset above. These simulate app activity logs from an imaginary music streaming app based on configuration settings.
The log files in the dataset you'll be working with are partitioned by year and month. For example, here are filepaths to two files in this dataset.

`log_data/2018/11/2018-11-12-events.json`

`log_data/2018/11/2018-11-13-events.json`

And below is an example of what the data in a log file, `2018-11-12-events.json`, looks like.

![log_file_example](/log_file_ex.png)

## Execution

Add the `aws_credentials` and `redshift` connections in Apache Airflow via Admin --> Connections

Trigger the `table_creation_dag` to setup Redshift with the tables required for the data pipeline 

Below is order of execution for the tasks in `sparkify_dag`

![sparkify_dag](/sparkify_dag.PNG)