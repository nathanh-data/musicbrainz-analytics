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

