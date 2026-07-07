-- ============================================================
-- ANALYTICS LAYER — MATERIALIZED VIEWS
-- ============================================================

-- artist_stats
DROP MATERIALIZED VIEW IF EXISTS analytics.artist_stats;
CREATE MATERIALIZED VIEW analytics.artist_stats AS
SELECT
    a.mbid AS artist_mbid,
    a.name AS artist_name,
    COUNT(DISTINCT rg.mbid) AS nb_albums,
    COUNT(DISTINCT ct.recording_mbid) AS nb_tracks,
    ROUND(AVG(ct.length_seconds), 2) AS avg_track_length_seconds,
    RANK() OVER (
        ORDER BY COUNT(DISTINCT rg.mbid) DESC
    ) AS rank_albums
FROM musicbrainz_raw.artist a
LEFT JOIN musicbrainz_raw.release_group rg
    ON a.mbid = rg.artist_mbid
LEFT JOIN musicbrainz_raw.release r
    ON rg.mbid = r.release_group_mbid
LEFT JOIN staging.clean_tracks ct
    ON r.mbid = ct.release_mbid
GROUP BY a.mbid, a.name;

-- albums
DROP MATERIALIZED VIEW IF EXISTS analytics.albums CASCADE;
CREATE MATERIALIZED VIEW analytics.albums AS
SELECT
    ca.release_group_mbid,
    ca.artist_mbid,
    a.name AS artist_name,
    ca.album_title,
    ca.first_release_date,
    ca.release_year,
    COUNT(DISTINCT ct.recording_mbid) AS nb_tracks,
    ROUND(AVG(ct.length_seconds), 2) AS avg_track_length_seconds,
    ROUND(SUM(ct.length_seconds), 2) AS total_album_length_seconds
FROM staging.clean_albums ca
LEFT JOIN musicbrainz_raw.artist a
    ON ca.artist_mbid = a.mbid
LEFT JOIN musicbrainz_raw.release r
    ON ca.release_group_mbid = r.release_group_mbid
LEFT JOIN staging.clean_tracks ct
    ON r.mbid = ct.release_mbid
GROUP BY
    ca.release_group_mbid,
    ca.artist_mbid,
    a.name,
    ca.album_title,
    ca.first_release_date,
    ca.release_year;

-- tracks
DROP MATERIALIZED VIEW IF EXISTS analytics.tracks CASCADE;
CREATE MATERIALIZED VIEW analytics.tracks AS
SELECT DISTINCT
    ct.recording_mbid,
    ct.track_title,
    a.mbid AS artist_mbid,
    a.name AS artist_name,
    rg.mbid AS release_group_mbid,
    rg.title AS album_title,
    rg.first_release_date,
    ROUND(ct.length_seconds, 2) AS track_length_seconds
FROM staging.clean_tracks ct
LEFT JOIN musicbrainz_raw.release r
    ON ct.release_mbid = r.mbid
LEFT JOIN musicbrainz_raw.release_group rg
    ON r.release_group_mbid = rg.mbid
LEFT JOIN musicbrainz_raw.artist a
    ON rg.artist_mbid = a.mbid;

-- data_quality_report
DROP MATERIALIZED VIEW IF EXISTS analytics.data_quality_report;
CREATE MATERIALIZED VIEW analytics.data_quality_report AS
SELECT
    CURRENT_TIMESTAMP AS report_date,
    COUNT(*) AS total_albums,
    COUNT(*) FILTER (WHERE nb_tracks = 0) AS albums_without_tracks,
    COUNT(*) FILTER (WHERE avg_track_length_seconds IS NULL) AS albums_without_duration,
    COUNT(*) FILTER (WHERE release_year IS NULL) AS albums_without_year,
    ROUND(
        COUNT(*) FILTER (WHERE release_year IS NULL)::numeric
        / NULLIF(COUNT(*), 0), 4
    ) AS pct_albums_without_year,
    ROUND(
        COUNT(*) FILTER (WHERE nb_tracks = 0)::numeric
        / NULLIF(COUNT(*), 0), 4
    ) AS pct_albums_without_tracks
FROM analytics.albums;

-- ============================================================
-- ANALYTICS LAYER — TABLES (non-materialized)
-- ============================================================

-- Non-materialized tables
-- These tables must be rebuilt after each pipeline execution.

-- artist_yearly
DROP TABLE IF EXISTS analytics.artist_yearly;
CREATE TABLE analytics.artist_yearly AS
SELECT
    a.mbid AS artist_mbid,
    a.name AS artist_name,
    CASE
        WHEN LEFT(rg.first_release_date, 4) ~ '^\d{4}$'
        THEN CAST(LEFT(rg.first_release_date, 4) AS INTEGER)
        ELSE NULL
    END AS release_year,
    COUNT(DISTINCT rg.mbid) AS nb_albums,
    COUNT(DISTINCT ct.recording_mbid) AS nb_tracks
FROM musicbrainz_raw.artist a
LEFT JOIN musicbrainz_raw.release_group rg
    ON a.mbid = rg.artist_mbid
LEFT JOIN musicbrainz_raw.release r
    ON rg.mbid = r.release_group_mbid
LEFT JOIN staging.clean_tracks ct
    ON r.mbid = ct.release_mbid
WHERE
    rg.first_release_date IS NOT NULL
    AND LEFT(rg.first_release_date, 4) ~ '^\d{4}$'
GROUP BY a.mbid, a.name, release_year;

-- dim_date
DROP TABLE IF EXISTS analytics.dim_date;
CREATE TABLE analytics.dim_date AS
SELECT DISTINCT
    release_year AS year,
    CONCAT(FLOOR(release_year / 10) * 10, 's') AS decade,
    CASE
        WHEN release_year < 1980 THEN 'Before 1980'
        WHEN release_year BETWEEN 1980 AND 1989 THEN '1980s'
        WHEN release_year BETWEEN 1990 AND 1999 THEN '1990s'
        WHEN release_year BETWEEN 2000 AND 2009 THEN '2000s'
        WHEN release_year BETWEEN 2010 AND 2019 THEN '2010s'
        ELSE '2020s'
    END AS era
FROM analytics.artist_yearly
WHERE release_year IS NOT NULL
ORDER BY year;

-- pipeline_monitoring
CREATE OR REPLACE VIEW analytics.pipeline_monitoring AS
SELECT
    run_id,
    pipeline_name,
    run_timestamp,
    status,
    rows_processed,
    execution_time_seconds
FROM staging.pipeline_runs;

-- ============================================================
-- ANALYTICS LAYER — INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_mv_albums_artist
    ON analytics.albums(artist_mbid);
CREATE INDEX IF NOT EXISTS idx_mv_albums_release_group
    ON analytics.albums(release_group_mbid);
CREATE INDEX IF NOT EXISTS idx_mv_albums_year
    ON analytics.albums(release_year);

CREATE INDEX IF NOT EXISTS idx_mv_tracks_artist
    ON analytics.tracks(artist_mbid);
CREATE INDEX IF NOT EXISTS idx_mv_tracks_album
    ON analytics.tracks(release_group_mbid);
CREATE INDEX IF NOT EXISTS idx_mv_tracks_recording
    ON analytics.tracks(recording_mbid);

CREATE INDEX IF NOT EXISTS idx_artist_yearly_artist
    ON analytics.artist_yearly(artist_mbid);
CREATE INDEX IF NOT EXISTS idx_artist_yearly_year
    ON analytics.artist_yearly(release_year);