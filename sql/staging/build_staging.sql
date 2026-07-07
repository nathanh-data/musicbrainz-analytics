-- ============================================================
-- STAGING LAYER — CLEAN TRACKS
-- ============================================================

DROP TABLE IF EXISTS staging.clean_tracks;
CREATE TABLE staging.clean_tracks AS
SELECT DISTINCT ON (t.recording_mbid)
    t.recording_mbid,
    t.title AS track_title,
    t.length / 1000.0 AS length_seconds,
    r.mbid AS release_mbid,
    rg.mbid AS release_group_mbid,
    rg.title AS album_title,
    a.mbid AS artist_mbid,
    a.name AS artist_name,
    rg.first_release_date
FROM musicbrainz_raw.track t
LEFT JOIN musicbrainz_raw.release r
    ON t.release_mbid = r.mbid
LEFT JOIN musicbrainz_raw.release_group rg
    ON r.release_group_mbid = rg.mbid
LEFT JOIN musicbrainz_raw.artist a
    ON rg.artist_mbid = a.mbid
WHERE t.length IS NOT NULL
ORDER BY t.recording_mbid, t.length DESC;

-- ============================================================
-- STAGING LAYER — CLEAN ALBUMS
-- ============================================================

DROP TABLE IF EXISTS staging.clean_albums;
CREATE TABLE staging.clean_albums AS
SELECT DISTINCT
    rg.mbid AS release_group_mbid,
    rg.artist_mbid,
    rg.title AS album_title,
    rg.first_release_date,
    CASE
        WHEN rg.first_release_date ~ '^\d{4}'
        THEN CAST(LEFT(rg.first_release_date, 4) AS INTEGER)
        ELSE NULL
    END AS release_year
FROM musicbrainz_raw.release_group rg
WHERE rg.title IS NOT NULL;