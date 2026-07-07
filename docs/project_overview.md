# 🎵 MusicBrainz Analytics

> **End-to-end data pipeline** extracting music data from the MusicBrainz API,
> storing it in PostgreSQL, and exposing analytical dashboards in Power BI.

> ⚠️ **Work in progress** — Currently running on a reduced dataset due to local
> storage constraints. Architecture is fully designed to scale.

---

## ⭐ Key Features

- MusicBrainz API ingestion with pagination support and configurable extraction limits
- PostgreSQL layered architecture (raw → staging → analytics)
- Materialized views for fast BI queries
- Scheduled execution via Windows Task Scheduler (Git Bash)
- Pipeline monitoring, execution history, observability & data quality reporting
- Power BI dashboards with drill-down capabilities

---

## 🛠️ Technologies Used

|     Category    |                      Technology                 |
|-----------------|-------------------------------------------------|
|     Language    |                        Python                   |
|     Database    |                     PostgreSQL                  |
|        API      |                MusicBrainz Public API           |
|        BI       |                   Power BI Desktop              |
|  Orchestration  | Windows Task Scheduler + Bash Script (Git Bash) |
| Version Control |                   Git / GitHub                  |

---

## 🧠 Data Engineering Concepts Demonstrated

- API ingestion with retry logic and rate limiting
- ELT architecture (Extract → Load → Transform)
- Data warehouse layering (raw / staging / analytics)
- PostgreSQL schema design (multi-layer)
- Data normalization and deduplication
- Incremental-ready pipeline design
- Materialized views for analytical performance
- SQL performance optimization (indexing strategy)
- Pipeline orchestration and scheduling
- Execution monitoring and observability
- Data quality reporting
- BI semantic modeling

---

## 🏗️ Architecture

```text
MusicBrainz API
      ↓
Raw Layer        (musicbrainz_raw — untransformed ingested data)
      ↓
Staging Layer    (staging — cleaned, normalized, deduplicated)
      ↓
Analytics Layer  (analytics — materialized views + tables, BI-ready)
      ↓
Power BI Dashboards
```

Execution flow:

```text
Windows Task Scheduler
        ↓
orchestration/run_pipeline.sh  (Git Bash)
        ↓
Python extraction → PostgreSQL ingestion
        ↓
Materialized views refresh
        ↓
logs/pipeline_YYYYMMDD_HHMMSS.log
```

---

## 🎼 Dataset Scope

Current dataset size depends on extraction parameters configured in the pipeline:

|            Parameter           |            Description            |
|--------------------------------|-----------------------------------|
|            Artists             | French artists only (area:France) |
|          Max artists           |   Configurable extraction limit   |
| Max release groups per artist  |   Configurable extraction limit   |
| Max releases per release group |   Configurable extraction limit   |

Current extraction limits are intentionally constrained for local development.
This controlled approach keeps the project lightweight while preserving a
realistic and production-grade data engineering architecture.

---

## 📈 Monitoring & Observability

The project includes operational monitoring features:

- Execution history tracking (status, duration, rows processed)
- Pipeline status monitoring (success / failure)
- Data quality KPIs (missing metadata detection)
- Dedicated Power BI monitoring dashboard

|               Object            |        Type       |             Purpose           |
|---------------------------------|-------------------|-------------------------------|
|     `staging.pipeline_state`    |       Table       | Last successful run timestamp |
|     `staging.pipeline_runs`     |       Table       |    Full execution history     |
| `analytics.pipeline_monitoring` |       Table       |  Aggregated monitoring KPIs   |
| `analytics.data_quality_report` | Materialized View |     Data completeness KPIs    |

### Operational KPIs

|                 KPI                  | Available |
|--------------------------------------|-----------|
|        Successful runs tracked       |    ✅    |
|          Failed runs tracked         |    ✅    |
| Average execution duration monitored |    ✅    |
|      Data quality KPIs available     |    ✅    |

---

## 📊 Power BI Dashboards

|       Dashboard         |                            Content                          |
|-------------------------|-------------------------------------------------------------|
|   **Overall Summary**   | Global KPIs, albums & tracks over time, artist bubble chart |
|   **Tree Structure**    |     Drill-down: artist → release year → album → track       |
| **Pipeline Monitoring** |      Run history, failure tracking, data quality report     |

### Power BI Semantic Model

```text
              dim_date
                  │
            artist_yearly
                  │
            artist_stats
             /        \
          albums      tracks

data_quality_report  (isolated)
pipeline_monitoring  (isolated)
```

Relationships are primarily built on:

- `artist_mbid` across artist, album and track analytics objects
- `artist_mbid` between `artist_yearly` and `artist_stats`
- `release_year` between `dim_date` and `artist_yearly`

---

## 🚀 Roadmap

- [ ] Docker containerization
- [ ] Prefect or Airflow orchestration
- [ ] Cloud deployment (AWS / Azure / GCP)
- [ ] Larger-scale ingestion
- [ ] Automated Power BI refresh via gateway
- [ ] CI/CD pipeline

---

## 🔧 Technical Implementation

### Database Layer

PostgreSQL database: `musicbrainz_db`

|     Schema        |                   Purpose                 |
|-------------------|-------------------------------------------|
| `musicbrainz_raw` |      Raw ingested data, untransformed     |
|    `staging`      | Cleaned, normalized and deduplicated data |
|    `analytics`    |    BI-ready aggregated views and tables   |

---

### Extraction Layer

Data extracted from the [MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API).

#### MusicBrainz data hierarchy

```text
Artist
  └── Release Group (Album)
        └── Release (Edition)
              └── Track
                    └── Recording
```

#### Extracted entities

|     Entity     |            Raw Table            |              Description             |
|----------------|---------------------------------|--------------------------------------|
|    Artists     |     `musicbrainz_raw.artist`    |   French artists (person or group)   |
| Release Groups | `musicbrainz_raw.release_group` | Albums only (`primary_type = Album`) |
|   Releases     |     `musicbrainz_raw.release`   |Physical/digital editions per album   |
|    Tracks      |     `musicbrainz_raw.track`     |           Tracks per release         |
|  Recordings    |   `musicbrainz_raw.recording`   |        Unique audio recordings       |
|    Labels      |     `musicbrainz_raw.label`     |       Record labels per release      |

#### API reliability features

- Retry logic (3 attempts per request)
- Timeout handling (10 seconds)
- Randomized wait times to avoid rate limiting
- Pagination on artists, release groups and releases

---

### Staging Layer

|           Table          |                        Purpose                     |
|--------------------------|----------------------------------------------------|
| `staging.clean_tracks`   |      Deduplicate tracks, convert ms → seconds      |
| `staging.clean_albums`   |   Normalize album metadata, extract release year   |
| `staging.pipeline_state` | Store last successful pipeline execution timestamp |
| `staging.pipeline_runs`  |   Full historical log of all pipeline executions   |

---

### Analytics Layer

Most analytical objects are implemented as **PostgreSQL materialized views**
for BI performance. Some supporting objects are standard tables.

|               Object            |          Type          |            Granularity           |                         Key Metrics                      |
|---------------------------------|------------------------|----------------------------------|----------------------------------------------------------|
|     `analytics.artist_stats`    |   Materialized View    |         1 row = 1 artist         |         nb albums, nb tracks, avg duration, rank         |
|        `analytics.albums`       |   Materialized View    |         1 row = 1 album          |         nb tracks, avg/total duration, release year      |
|        `analytics.tracks`       |   Materialized View    |         1 row = 1 track          |               title, artist, album, duration             |
| `analytics.data_quality_report` |   Materialized View    |         Global snapshot          |                    missing metadata KPIs                 |
|    `analytics.artist_yearly`    |         Table          |     1 row = 1 artist × 1 year    |                  albums & tracks per year                |
| `analytics.pipeline_monitoring` |         Table          |         Global snapshot          |               run count, failures, avg duration          |
|      `analytics.dim_date`       |         Table          |         Date dimension           |                      year, decade, era                   |

Materialized views are refreshed via:

```text
sql/materialized_views/refresh_views.sql
```

---

### Indexing Strategy

Indexes were added on frequently used join keys and analytical dimensions
to improve PostgreSQL query performance and Power BI refresh speed.

Key indexes include:

|                    Column                    |         Purpose        |
|----------------------------------------------|------------------------|
| `musicbrainz_raw.release_group.artist_mbid`  | Artist → albums join   |
| `musicbrainz_raw.release.release_group_mbid` | Album → releases join  |
| `musicbrainz_raw.track.release_mbid`         | Release → tracks join  |
| `musicbrainz_raw.track.recording_mbid`       | Track → recording join |
| `analytics.albums.artist_mbid`               | BI artist filtering    |
| `analytics.albums.release_year`              | BI time filtering      |
| `analytics.tracks.artist_mbid`               | BI track filtering     |
| `analytics.artist_yearly.release_year`       | BI yearly filtering    |

Benefits: faster joins, improved materialized view refresh, faster Power BI loading.

---

### Monitoring Layer

Pipeline execution is tracked automatically at each run.

Each execution:
- updates `staging.pipeline_state` with the last successful run timestamp
- inserts a row in `staging.pipeline_runs` with status, duration and row count
- writes a timestamped log file under `logs/`

---

### Power BI Layer

Power BI Desktop connects directly to PostgreSQL analytics objects via native connector.

Relationships are primarily built on:
- `artist_mbid` across artist, album and track analytics objects
- `artist_mbid` between `artist_yearly` and `artist_stats`
- `release_year` between `dim_date` and `artist_yearly`

---

## ⚠️ Current Limitations

|                             Limitation                              |                             Detail                            |
|---------------------------------------------------------------------|---------------------------------------------------------------|
|                         Reduced dataset                             | Constrained by configurable extraction limits (local storage) |
|                       No delta extraction                           |         MusicBrainz API does not expose change timestamps     |
|                        Scheduled refresh                            |       Materialized views refreshed at each pipeline run       |
|                       Local infrastructure                          |                    No cloud deployment yet                    |

---

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/your-username/musicbrainz-analytics.git
cd musicbrainz-analytics
```

### 2. Set up the environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a .env file based on .env.example and update the database credentials.
```env
DB_NAME=musicbrainz_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Run the pipeline manually

```bash
python scripts/extraction/api_musicbrainz.py
```

### 5. Refresh materialized views

```sql
-- Run in pgAdmin or psql
\i sql/materialized_views/refresh_views.sql
```

### 6. Automated execution (optional)

Configure Windows Task Scheduler to run `orchestration/run_pipeline.sh` via Git Bash
on your desired schedule.

---

## 📁 Project Structure

## 📁 Project Structure

```text
musicbrainz-analytics/
├── data/
│   ├── analytics/                   # Analytics output data
│   ├── raw/                         # Raw ingested data
│   └── staging/                     # Staged/cleaned data
├── docs/
│   ├── troubleshooting/
│   │   └── psycopg2_encoding_error.md
│   ├── architecture.md
│   ├── data_sources.md
│   ├── known_limitations.md         # Known limitations & engineering notes
│   ├── project_overview.md
│   └── roadmap.md
├── logs/                            # Timestamped execution logs
├── notebooks/                       # Exploratory notebooks
├── orchestration/
│   └── run_pipeline.sh              # End-to-end orchestration (Git Bash)
├── powerbi/                         # Power BI dashboard files
├── scripts/
│   ├── extraction/
│   │   └── api_musicbrainz.py       # API extraction pipeline
│   ├── transformation/              # SQL/Python transformation scripts
│   └── test_connection.py           # Database connection test
├── sql/
│   ├── analytics/
│   │   └── build_analytics.sql      # Materialized views, analytics tables, indexes
│   ├── materialized_views/
│   │   └── refresh_views.sql        # Materialized view refresh only
│   ├── staging/
│   │   └── build_staging.sql        # Staging table construction
│   └── setup_database.sql           # Schema creation, raw tables, indexes
├── .env.example                     # Environment variables template (not versioned)
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```