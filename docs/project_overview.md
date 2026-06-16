# Project Overview

## 🎯 Objectif

Créer un pipeline data permettant :

1. D’extraire les données MusicBrainz
2. De les stocker dans PostgreSQL
3. De les transformer
4. De créer des analyses sur les artistes français

## 🧱 Étapes

1. Setup projet
2. Import base MusicBrainz
3. Transformation des données
4. Création tables analytiques
5. Visualisation Power BI

## 📊 Résultat attendu

Un dashboard Power BI avec :

- Top artistes
- Nombre d’albums
- Collaborations
- Labels dominants



⚙️ Current Implementation

✅ Step 1 — Project Setup
Python environment (venv)
PostgreSQL connection via psycopg
Environment variables with .env

✅ Step 2 — Database Setup
PostgreSQL database created (musicbrainz_db)
Schemas created:
musicbrainz_raw
staging
analytics

✅ Step 3 — Data Extraction (API)

Data is extracted from the MusicBrainz API and stored in raw tables.

🔹 Artists
Fetch French artists via API (area:France)
Insert into musicbrainz_raw.artist
Deduplication using MBID (primary key)

🔹 Release Groups (Albums)
Fetch albums per artist
Filter only primary_type = 'Album'
Insert into musicbrainz_raw.release_group

🔹 Recordings (Tracks)
Fetch recordings per artist
Insert into musicbrainz_raw.recording

🔹 Labels
Extracted indirectly via releases (MusicBrainz structure)
Insert into musicbrainz_raw.label

⚠️ Notes
API rate limiting respected (1 request/sec)
Pagination not yet implemented (limit=100)
Some fields may be NULL (normal for MusicBrainz data)


⚙️ Step 4 — Analytics Layer (NEW)

The project now includes a full analytical layer built on top of raw MusicBrainz data.

📊 analytics.artist_stats

Aggregated table at artist level:

Number of albums per artist
Number of recordings per artist
Average recording length
Artist ranking based on productivity

👉 Used for:

artist comparison
productivity analysis
Power BI top-level KPIs
📀 analytics.albums

Aggregated table at album level:

Number of recordings per album
Average track duration per album

👉 Used for:

album comparison
content richness analysis
album-level KPIs in Power BI
🧠 Data modeling approach

The analytics layer is built using SQL aggregations on top of raw tables:

musicbrainz_raw.artist
musicbrainz_raw.release_group
musicbrainz_raw.recording

👉 This introduces:

star schema-like structure
separation between raw and analytical data
BI-ready datasets
⚠️ Notes
Album-level metrics are approximated at artist level in current version
Future improvement: full track → album mapping via release hierarchy
API rate limiting respected (1 request/sec)


🔹 Improved Data Model

Implemented proper MusicBrainz hierarchy:

release_group → release → track → recording

This enables accurate album-level analytics (track count, duration, etc.)


## ⚙️ Step 5 — Staging Layer (NEW)

A staging layer was introduced to clean and normalize raw MusicBrainz data before analytics.

### 📀 staging.clean_tracks

Purpose:

- deduplicate tracks
- normalize durations
- prepare BI-ready track-level data

Key transformations:

- remove duplicated recordings within same release
- convert track duration from milliseconds to seconds
- standardize track structure

This staging layer improves data quality before aggregation.

---

## ⚙️ Step 6 — Extended Analytics Layer (NEW)

The analytics layer now includes multiple granularities:

### 👤 analytics.artist_stats

1 row = 1 artist

Contains:

- number of albums
- number of tracks
- average track duration
- artist productivity ranking

Used for:

- top artist KPIs
- productivity analysis
- ranking dashboards

---

### 📀 analytics.albums

1 row = 1 album

Contains:

- album title
- artist
- release date
- number of tracks
- average track duration
- total album duration

Used for:

- album comparison
- catalog analysis
- duration analytics

---

### 🎵 analytics.tracks

1 row = 1 track

Contains:

- track title
- artist
- album
- track duration
- release year

Used for:

- detailed track analysis
- longest tracks
- track-level BI dashboards

---

### 📅 analytics.artist_yearly

1 row = 1 artist + 1 year

Contains:

- albums released per year
- tracks released per year

Used for:

- temporal analysis
- artist evolution over time
- yearly productivity dashboards

---

## 🧠 Current Data Model

The project now follows a layered architecture:

### Raw Layer

musicbrainz_raw.artist
musicbrainz_raw.release_group
musicbrainz_raw.release
musicbrainz_raw.track
musicbrainz_raw.recording
musicbrainz_raw.label

### Staging Layer

staging.clean_tracks

### Analytics Layer

analytics.artist_stats
analytics.albums
analytics.tracks
analytics.artist_yearly

---

## 🔗 MusicBrainz Hierarchy

The project now implements the full MusicBrainz hierarchy:

artist
→ release_group (album)
→ release
→ track
→ recording

This enables accurate album-level and track-level analytics.

---

## 📊 Power BI Integration

Power BI is connected directly to PostgreSQL analytics tables.

Implemented dashboards include:

- artist productivity
- album statistics
- track analysis
- yearly evolution

The data model follows BI best practices with hierarchical relationships between:
artist → albums → tracks



## ⚠️ Current Data Limitations

The current pipeline uses the MusicBrainz API with limited extraction scope.

Known limitations:

- Only the top 50 French artists are currently extracted
- API pagination is not yet implemented
- Some releases do not contain track metadata
- Community-driven MusicBrainz data may contain missing fields
- Data quality KPIs reflect ingested data only




## ⚙️ API Improvements (NEW)

The extraction pipeline now supports API pagination for:

- artists
- release groups
- releases

This enables scalable extraction while controlling local storage usage.

Current extraction strategy includes configurable limits:

- max artists
- max release groups per artist
- max releases per album

This allows progressive scaling of the project.





### 📀 staging.clean_albums

Purpose:

- normalize album metadata
- extract release year
- improve BI joins
- prepare dimensional modeling

Key transformations:

- release year extraction
- duplicate prevention
- standardized album structure





### 📋 analytics.data_quality_report

Purpose:

Monitor ingestion quality and missing metadata.

Contains KPIs such as:

- albums without tracks
- albums without duration
- albums without release year

Used for:

- pipeline monitoring
- data validation
- BI quality reporting





### 📅 analytics.dim_date

Purpose:

Centralized date dimension for Power BI time intelligence.

Used for:

- yearly filtering
- timeline interactions
- temporal dashboard analysis

This improves Power BI relationship modeling.





## 🚀 Scalability Strategy

Due to MusicBrainz data volume, the project currently uses controlled extraction limits.

The architecture is designed to progressively scale through:

- pagination
- incremental loading
- PostgreSQL indexing
- materialized views
- future orchestration tools




## ⚙️ Step 7 — SQL Industrialization (NEW)

The project now includes several industrialization features inspired by real-world data engineering workflows.

---

### ⚡ PostgreSQL Indexing

Indexes were added on key columns to improve query performance and Power BI refresh speed.

Examples:

* artist_mbid
* release_group_mbid
* recording_mbid
* release_year

Benefits:

* faster joins
* faster aggregations
* improved dashboard responsiveness
* scalable analytical queries

---

### 🧱 Materialized Views

The analytics layer was migrated from standard tables to PostgreSQL materialized views.

Implemented materialized views:

* analytics.artist_stats
* analytics.albums
* analytics.tracks

Benefits:

* precomputed aggregations
* faster BI queries
* reduced Power BI load time
* closer to production-grade analytics architecture

Materialized views are refreshed manually through a dedicated SQL script.

---

### 🔄 Refresh Strategy

A centralized SQL refresh script was implemented:

sql/materialized_views/refresh_views.sql

This script refreshes all analytical materialized views in the correct order.

Benefits:

* easier maintenance
* reproducible refresh process
* orchestration-ready architecture

---

### 📈 Incremental-Ready Pipeline

The extraction pipeline now tracks execution state using:

staging.pipeline_state

This table stores:

* pipeline name
* last successful run timestamp

The Python pipeline now:

* reads previous execution state
* updates last execution timestamp automatically
* prepares future incremental loading strategies

Although MusicBrainz API does not fully support delta extraction, the project architecture is now incremental-ready.

---

### 🛡️ Pipeline Reliability Improvements

The extraction pipeline now includes:

* retry logic
* timeout handling
* randomized wait times
* API rate-limit protection
* safer HTTP requests

Benefits:

* improved stability
* reduced API failures
* safer long-running ingestion jobs

---

## 🧠 Current Architecture Maturity

The project now follows a layered and industrialized ELT architecture:

API Extraction
→ Raw Layer
→ Staging Layer
→ Analytics Materialized Views
→ Power BI

Key engineering concepts implemented:

* layered data architecture
* dimensional modeling
* SQL transformations
* indexing strategy
* materialized views
* incremental-ready ingestion
* data quality monitoring
* BI-ready semantic layer

This architecture is designed to progressively evolve toward:

* orchestration (cron / Prefect / Airflow)
* cloud deployment
* larger-scale ingestion
* automated refresh pipelines




## ⚙️ Step 8 — Pipeline Monitoring & Orchestration (NEW)

The project now includes a complete monitoring and orchestration layer inspired by production-grade data pipelines.

---

### 🔄 Automated Pipeline Execution

A centralized orchestration script was implemented:

```text
orchestration/run_pipeline.sh
```

This script automatically:

1. launches the extraction pipeline
2. loads MusicBrainz data into PostgreSQL
3. refreshes materialized views
4. stores execution logs

Benefits:

* repeatable execution
* simplified maintenance
* production-like workflow

---

### ⏰ Task Scheduling

Pipeline execution is automated using Windows Task Scheduler.

Current workflow:

```text
Task Scheduler
        ↓
run_pipeline.sh
        ↓
Python Extraction
        ↓
PostgreSQL
        ↓
Materialized Views Refresh
        ↓
Monitoring Tables
        ↓
Power BI
```

Benefits:

* fully automated refresh
* scheduled ingestion
* reduced manual operations

---

### 📋 Execution Logging

Each pipeline execution generates a dedicated log file.

Location:

```text
logs/
```

Example:

```text
pipeline_20260611_174048.log
```

Logs contain:

* execution start time
* extraction progress
* errors
* refresh status
* execution end time

Benefits:

* troubleshooting
* auditability
* operational monitoring

---

### 📊 Pipeline Monitoring

Pipeline executions are tracked inside PostgreSQL.

#### staging.pipeline_state

Stores:

* pipeline name
* last successful execution timestamp

Used for:

* incremental-ready architecture
* execution tracking

---

#### staging.pipeline_runs

Stores historical executions:

* execution timestamp
* execution status
* processed rows
* execution duration

Used for:

* operational monitoring
* SLA tracking
* performance analysis

---

### 📈 Monitoring Analytics

Additional analytical objects were introduced.

#### analytics.pipeline_monitoring

Provides monitoring KPIs such as:

* total executions
* successful executions
* failed executions
* average execution duration
* latest execution status

Used for:

* operational dashboards
* pipeline health monitoring

---

#### analytics.data_quality_report

Provides data quality KPIs such as:

* albums without tracks
* albums without duration
* albums without release year
* quality percentages

Used for:

* ingestion validation
* data completeness tracking
* BI quality dashboards

---

### 📊 Power BI Monitoring Dashboard

A dedicated monitoring dashboard was added.

Includes:

* pipeline status KPIs
* execution history
* execution duration trends
* data quality indicators

Benefits:

* end-to-end observability
* operational visibility
* production-style monitoring

---

## 🚀 Current Project Maturity

The project now implements most core Data Engineering concepts:

* API ingestion
* PostgreSQL storage
* layered architecture
* SQL transformations
* staging layer
* analytics layer
* indexing strategy
* materialized views
* automated refresh
* orchestration
* monitoring
* data quality reporting
* Power BI dashboards

The architecture is designed to evolve toward:

* Docker deployment
* CI/CD pipelines
* Prefect orchestration
* Apache Airflow
* Cloud infrastructure (AWS / Azure / GCP)
* Larger-scale data ingestion
