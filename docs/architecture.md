# Architecture

## Pipeline

MusicBrainz
↓
PostgreSQL (raw)
↓
Transformations SQL
↓
Tables analytics
↓
Power BI

## Schémas

- raw : données brutes MusicBrainz
- staging : nettoyage
- analytics : tables finales