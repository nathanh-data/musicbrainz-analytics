# Architecture

## Global Architecture

MusicBrainz API
        ↓
Python Extraction Pipeline
        ↓
musicbrainz_raw
        ↓
staging
        ↓
analytics
(materialized views + analytics tables)
        ↓
Power BI


---

## Layer Description

### MusicBrainz API

External data source used to retrieve:

* artists
* albums
* releases
* tracks

The extraction process uses the official MusicBrainz REST API with pagination and rate limiting.

---

### Python Extraction Pipeline

Responsible for:

* API calls
* pagination management
* error handling
* loading data into PostgreSQL
* execution logging

Main file:

```text
scripts/extraction/api_musicbrainz.py
```

---

### Raw Layer (`musicbrainz_raw`)

Stores data exactly as received from MusicBrainz.

Main tables:

* artist
* release_group
* release
* track
* recording
* label

Purpose:

* preserve source data
* allow reprocessing
* ensure traceability

---

### Staging Layer (`staging`)

Intermediate transformation layer.

Main tables:

* pipeline_state
* pipeline_runs
* clean_tracks
* clean_albums

Purpose:

* data cleaning
* normalization
* monitoring
* preparation for analytics

---

### Analytics Layer (`analytics`)

Business-oriented analytical datasets.

Main objects:

* artist_stats
* albums
* tracks
* artist_yearly
* data_quality_report
* pipeline_monitoring
* dim_date

Purpose:

* KPI computation
* reporting
* dashboard consumption

---

### Materialized Views

Used to improve query performance.

Current materialized views:

* artist_stats
* albums
* tracks
* data_quality_report

Refreshed automatically after each pipeline execution.

---

### Power BI

Visualization layer connected directly to PostgreSQL.

Dashboards include:

* artist productivity
* album statistics
* track analysis
* pipeline monitoring
* data quality monitoring

---

## Orchestration

Pipeline execution is automated through:

* Bash script (`run_pipeline.sh`)
* Windows Task Scheduler

The workflow:

1. Launch extraction pipeline
2. Load PostgreSQL tables
3. Refresh materialized views
4. Log execution status
5. Update monitoring tables

---

## Monitoring

Monitoring is implemented using:

### staging.pipeline_state

Stores the latest successful pipeline execution.

### staging.pipeline_runs

Stores historical executions:

* execution date
* status
* execution time
* processed rows

### analytics.pipeline_monitoring

Provides aggregated monitoring KPIs for Power BI.

### analytics.data_quality_report

Tracks data completeness and quality metrics.
