# 📊 Project Roadmap — MusicBrainz Analytics

## 🎯 Project Goal

Build a complete data engineering pipeline to analyze French music artists
using MusicBrainz data, PostgreSQL, and Power BI.

---

## 🧠 Global Vision

This project is designed in two phases:

- **Phase 1:** Lightweight pipeline using the MusicBrainz API (low storage, fully operational)
- **Phase 2:** Full-scale pipeline using the complete MusicBrainz database dump

---

## 🚧 Phase 1 — API-Based Pipeline (Current)

### Architecture

```text
MusicBrainz API
      ↓
Python extraction (pagination, retry logic, rate limiting)
      ↓
PostgreSQL — musicbrainz_raw schema
      ↓
Staging layer (cleaning, normalization, deduplication)
      ↓
Analytics layer (materialized views + analytics tables)
      ↓
Power BI dashboards
```

### What was built

|                 Component               | Status |
|-----------------------------------------|--------|
|          API extraction pipeline        | ✅ |
|           Raw PostgreSQL schema         | ✅ |
|               Staging layer             | ✅ |
|       Analytics materialized views      | ✅ |
|             Indexing strategy           | ✅ |
| Pipeline orchestration (Task Scheduler) | ✅ |
|     Execution monitoring & logging      | ✅ |
|         Data quality reporting          | ✅ |
|           Power BI dashboards           | ✅ |

### Current Limitations

|       Limitation     |                            Detail                         |
|----------------------|-----------------------------------------------------------|
| Partial dataset      | Configurable extraction limits (local storage constraint) |
| No delta extraction  |     MusicBrainz API does not expose change timestamps     |
| Local infrastructure |                   No cloud deployment yet                 |

---

## 🏗️ Phase 2 — Full Data Engineering Pipeline (Planned)

### Objective

Replace the API extraction layer with a full MusicBrainz database dump ingestion,
while keeping all downstream transformations and dashboards unchanged.

### Architecture

```text
MusicBrainz Database Dump (~100GB)
      ↓
PostgreSQL — musicbrainz_raw schema
      ↓
Staging layer (unchanged)
      ↓
Analytics layer (unchanged)
      ↓
Power BI dashboards (unchanged)
```

### What changes vs Phase 1

|   Layer    |            Change            |
|------------|------------------------------|
| Extraction |  API → full dump ingestion   |  
| Raw schema | Same structure, full dataset |
| Staging    |          No change           |
| Analytics  |          No change           |
| Power BI   |          No change           |

### Constraints

- High storage requirements (~100GB+)
- More complex initial setup
- Requires external disk or cloud storage

---

## 🔁 Migration Strategy

The project is intentionally designed to allow an easy transition from API to
full database dump, following a key architectural principle:

> **Separate the data source from the data transformation.**

This means the entire staging and analytics stack can be reused as-is when
migrating to the full dataset.

---

## 🚀 Next Planned Improvements

### Engineering

- [ ] Docker containerization
- [ ] Prefect or Airflow orchestration
- [ ] Automated testing
- [ ] CI/CD with GitHub Actions
- [ ] Cloud deployment (AWS / Azure / GCP)

### Data

- [ ] Replace REST API extraction with the official MusicBrainz database dump
- [ ] Improve artist attribution using `artist_release_group.is_track_artist`
- [ ] Remove compilation bias from artist-level KPIs
- [ ] Larger-scale ingestion (500+ artists)
- [ ] Delta / incremental loading strategy
- [ ] Support complete MusicBrainz dataset (~100GB)

### BI & Monitoring

- [ ] Automated Power BI refresh via gateway
- [ ] Extended data quality KPIs
- [ ] Additional Power BI dashboard pages

---

## 💡 Why This Approach?

- **Start simple** → deliver a working pipeline fast
- **Scale progressively** → simulate real-world data engineering constraints
- **Maximize reusability** → transformations and dashboards survive a data source change
- **Portfolio value** → demonstrates end-to-end data engineering thinking