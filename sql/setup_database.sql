-- This script creates the database structure only.
-- It does not create staging tables or analytics objects.

-- ============================================================
-- SCHEMA CREATION
-- ============================================================

CREATE SCHEMA IF NOT EXISTS musicbrainz_raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS analytics;

-- ============================================================
-- RAW LAYER — TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS musicbrainz_raw.artist (
    mbid TEXT PRIMARY KEY,
    name TEXT,
    country TEXT,
    disambiguation TEXT,
    type TEXT
);

CREATE TABLE IF NOT EXISTS musicbrainz_raw.release_group (
    mbid TEXT PRIMARY KEY,
    artist_mbid TEXT,
    title TEXT,
    primary_type TEXT,
    first_release_date TEXT,
    FOREIGN KEY (artist_mbid) REFERENCES musicbrainz_raw.artist(mbid)
);

CREATE TABLE IF NOT EXISTS musicbrainz_raw.release (
    mbid TEXT PRIMARY KEY,
    release_group_mbid TEXT,
    title TEXT,
    FOREIGN KEY (release_group_mbid) REFERENCES musicbrainz_raw.release_group(mbid)
);

CREATE TABLE IF NOT EXISTS musicbrainz_raw.track (
    mbid TEXT PRIMARY KEY,
    release_mbid TEXT,
    recording_mbid TEXT,
    title TEXT,
    length INTEGER,
    FOREIGN KEY (release_mbid) REFERENCES musicbrainz_raw.release(mbid)
);

-- ============================================================
-- STAGING LAYER — TABLES
-- ============================================================

CREATE TABLE IF NOT EXISTS staging.pipeline_state (
    pipeline_name TEXT PRIMARY KEY,
    last_run TIMESTAMP
);

CREATE TABLE IF NOT EXISTS staging.pipeline_runs (
    run_id SERIAL PRIMARY KEY,
    pipeline_name TEXT,
    run_timestamp TIMESTAMP,
    status TEXT,
    rows_processed INTEGER,
    execution_time_seconds NUMERIC
);

INSERT INTO staging.pipeline_state (pipeline_name, last_run)
VALUES ('musicbrainz_api', NULL)
ON CONFLICT (pipeline_name) DO NOTHING;

-- ============================================================
-- RAW LAYER — INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_artist_name
    ON musicbrainz_raw.artist(name);

CREATE INDEX IF NOT EXISTS idx_release_group_artist
    ON musicbrainz_raw.release_group(artist_mbid);

CREATE INDEX IF NOT EXISTS idx_release_release_group
    ON musicbrainz_raw.release(release_group_mbid);

CREATE INDEX IF NOT EXISTS idx_track_release
    ON musicbrainz_raw.track(release_mbid);

CREATE INDEX IF NOT EXISTS idx_track_recording
    ON musicbrainz_raw.track(recording_mbid);