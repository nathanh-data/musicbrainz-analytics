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