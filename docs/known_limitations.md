# Known Limitations & Engineering Notes

This document describes limitations identified during development,
their root causes, and the decisions made to address them.

---

## MusicBrainz REST API — Artist Attribution

### Observation

During dashboard validation, artist-level KPIs appeared inconsistent.

Example:

| Artist | Albums (observed) | Expected |
|---|---|---|
| Claude Debussy | 1,539 | ~80–100 |
| Richard Clayderman | 19 | 100+ |

### Investigation

The issue was not caused by the SQL transformations or the ETL pipeline.

Three hypotheses were tested in order:

**Hypothesis 1 — Database pollution from previous runs**
Old pipeline runs without extraction limits had loaded data using
`ON CONFLICT DO NOTHING`, meaning previous unconstrained data was
never overwritten. A full `TRUNCATE` + pipeline restart was performed.

Result: album counts remained inconsistent → hypothesis rejected.

**Hypothesis 2 — SQL aggregation error**
Direct queries confirmed that `analytics.artist_stats` correctly
reflects the content of `musicbrainz_raw.release_group`.
No duplicates were found.

Result: SQL layer is correct → hypothesis rejected.

**Hypothesis 3 — API behavior**
The MusicBrainz REST API endpoint `/release-group?artist=mbid` returns
every release group associated with the artist, including:

- compilation albums
- releases where the artist appears on only one track
- re-editions and remasters credited to the artist

The API does not provide enough information to distinguish:
- primary album artist
- track contributor or secondary credited artist

### Root Cause

The `artist_release_group.is_track_artist` field exists in the full
MusicBrainz database and would allow correct filtering. However, this
field is **not exposed through the REST API**.

Adding `inc=artist-credits` to the API request was tested and confirmed
to return no additional attribution data for the `/release-group` endpoint.

This information is only available in the official MusicBrainz database dump, not through the public REST API.

### Decision

Rather than introducing heuristic SQL filters based on title patterns
(e.g. filtering titles containing `/` or `&`), the project intentionally
preserves the original API data and documents this limitation.

Heuristic filters would:
- remove legitimate albums with similar title patterns
- introduce silent data quality issues
- be fragile and difficult to maintain

### Planned Resolution

Phase 2 will replace the REST API with the official MusicBrainz database
dump. This will enable:

- accurate artist attribution via `artist_release_group.is_track_artist`
- removal of compilation bias from artist-level KPIs
- correct album counts for classical composers and prolific artists

---

## Engineering Challenges

### Challenge Summary

| Challenge | Solution Implemented |
|---|---|
| API rate limiting | Retry logic + randomized delay + pagination |
| Duplicate recordings | `DISTINCT ON (recording_mbid)` in staging |
| Missing release year | Regex validation + `CAST` to integer |
| Credential management | `.env` file + `.env.example` committed |
| Pipeline monitoring | `staging.pipeline_runs` + Power BI dashboard |
| Data quality tracking | `analytics.data_quality_report` materialized view |
| SQL maintainability | Separated `setup` / `build_staging` / `build_analytics` / `refresh` |

---

### API Rate Limiting

MusicBrainz enforces strict rate limits on its public REST API.

Implemented solutions:

- retry logic with 3 attempts per request
- randomized wait time between requests (`1 + random(0, 0.5)` seconds)
- longer pause on failure (`2 + random(0, 1)` seconds)
- pagination on all endpoints (artists, release groups, releases)
- configurable extraction limits to control request volume

---

### Duplicate Recordings

Multiple releases of the same album (editions, remasters, digital versions)
can contain identical recordings with the same `recording_mbid`.

Without deduplication, track-level aggregations would be inflated.

Resolved in `staging.clean_tracks` using PostgreSQL `DISTINCT ON`:

```sql
SELECT DISTINCT ON (t.recording_mbid)
    ...
FROM musicbrainz_raw.track t
...
ORDER BY t.recording_mbid, t.length DESC;
```

This keeps one occurrence per unique recording, prioritizing the entry
with the longest available duration.

---

### Missing or Inconsistent Release Dates

MusicBrainz release dates can be stored in multiple formats:

- `YYYY-MM-DD` (full date)
- `YYYY-MM` (partial)
- `YYYY` (year only)
- `NULL` (missing)

A regex-based validation was implemented in staging to safely extract
the release year:

```sql
CASE
    WHEN rg.first_release_date ~ '^\d{4}'
    THEN CAST(LEFT(rg.first_release_date, 4) AS INTEGER)
    ELSE NULL
END AS release_year
```

Albums with no valid year are preserved in the dataset but excluded
from time-based analytics.

---

### SQL Maintainability

Early development mixed schema creation, staging builds, analytics builds
and refresh operations into a single file. This violated the DRY principle
and made maintenance error-prone.

The SQL layer was reorganized into four distinct files with clear responsibilities:

| File | Responsibility |
|---|---|
| `setup_database.sql` | Schema creation, raw tables, indexes |
| `build_staging.sql` | Staging table construction |
| `build_analytics.sql` | Materialized views, analytics tables, indexes |
| `refresh_views.sql` | Materialized view refresh only |

This structure allows the entire database to be rebuilt by executing the SQL files in sequence,
and allows incremental refresh without touching the schema.

---

### Credential Management

Database credentials are managed through a `.env` file loaded by Python
via `python-dotenv`. A `.env.example` file is committed to the repository
to document required variables without exposing sensitive values:

```env
DB_NAME=musicbrainz_db
DB_USER=your_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```


## Lessons Learned

One of the main lessons from this project is that incorrect analytical
results are not always caused by SQL logic or ETL transformations.

When building data pipelines, understanding the semantics and limitations
of the source system is just as important as designing the pipeline itself.

This investigation highlighted the importance of validating assumptions
against the source data before implementing corrective transformations.