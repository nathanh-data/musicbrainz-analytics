# Data Sources

## MusicBrainz

MusicBrainz is an open-source music encyclopedia that collects music metadata
and makes it available to the public.

### Useful Links

- **Database Schema:** https://musicbrainz.org/doc/MusicBrainz_Database/Schema
  → Understand the structure of core entities (artist, release, recording...)

- **Beginner Guide:** https://musicbrainz.org/doc/Beginners_Guide
  → Introduction to how MusicBrainz works

- **Database:** https://musicbrainz.org/doc/MusicBrainz_Database
  → Information about database dumps and replication

- **API Documentation:** https://musicbrainz.org/doc/MusicBrainz_API
  → REST API reference used in this project

---

## Usage in this Project

The MusicBrainz API is used to extract the following entities:

|     Entity     |             Raw Table           |               Description           |
|----------------|---------------------------------|-------------------------------------|
|     Artists    |     `musicbrainz_raw.artist`    |   French artists (person or group)  |
| Release Groups | `musicbrainz_raw.release_group` |              Albums only            |
|     Releases   |    `musicbrainz_raw.release`    | Physical/digital editions per album |
|      Tracks    |     `musicbrainz_raw.track`     |          Tracks per release         |
|    Recordings  |   `musicbrainz_raw.recording`   |        Unique audio recordings      |
|      Labels    |     `musicbrainz_raw.label`     |       Record labels per release     |

The extracted data is loaded into the `musicbrainz_raw` schema before being
transformed through the `staging` and `analytics` layers.

---

## Current Extraction Scope

- French artists only (`area:France`)
- Configurable extraction limits (artists, release groups, releases)
- Album-focused dataset (`primary_type = Album`)

Extraction limits are intentionally constrained for local development.
The architecture is designed to scale progressively.

---

## Architecture Flexibility

The project is intentionally designed so that the MusicBrainz API source
can later be replaced by the full MusicBrainz database dump without
changing any downstream transformations or Power BI dashboards.

What would change:
- Data extraction layer (API → dump ingestion)

What would stay the same:
- `musicbrainz_raw` schema structure
- Staging transformations
- Analytics materialized views
- Power BI dashboards and semantic model