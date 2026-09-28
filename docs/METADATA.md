# Deposit Metadata (Zenodo / Figshare / GitHub)

Ready-to-paste metadata for repository deposit forms. Copy each field into the
corresponding box; nothing here requires editing except the two placeholders noted
at the end.

---

## Title

**Short form** (use if the form has a tight character limit)

```
Redis Cache Strategy Benchmark: Cache-Aside vs. Read-Through in Spring Boot
```

**Full form** (preferred)

```
Redis Cache Strategy Benchmark: Cache-Aside vs. Framework-Managed Read-Through in Spring Boot under Concurrent Load
```

---

## Description / Abstract

```
A controlled benchmark dataset comparing two server-side caching strategies in a
Spring Boot application backed by Redis and MySQL: explicit Cache-Aside, where the
application performs GET/SET operations directly, and framework-managed Read-Through,
where Spring Cache handles caching through @Cacheable.

Both strategies run in the same application process with an identical repository
layer, SQL, Redis key format, TTL, JSON serialization, and request sequence, so that
measured differences reflect the caching access pattern rather than incidental
implementation drift.

Design: 2 strategies x 3 concurrency levels (25, 50, 100) x 5 repetitions = 30
independent runs. Each run consists of a 15 s warm-up followed by a 60 s measurement
window. Measurements were taken in a verified Hot Cache steady state, with zero
database loads and zero cache misses during every measurement window.

Contents: an analysis-ready run-level table (30 rows), per-run application probe
snapshots, a full statistical analysis (model coefficients with heteroskedasticity-
robust standard errors, effect sizes with bootstrap confidence intervals, assumption
tests, and leave-one-out robustness checks), the JMeter test plan, and the analysis
script. The complete request-level data comprises 11,325,558 request records and is
distributed as a compressed archive alongside tagged releases.

All 30 runs passed seven automated validity gates; zero runs were invalidated and zero
request errors were recorded.

Keywords: Redis, caching, cache-aside, read-through, Spring Boot, Spring Cache,
benchmark, performance measurement, concurrent load.
```

---

## Keywords

```
Redis; caching; cache-aside; read-through; Spring Boot; Spring Cache; benchmark; performance measurement; concurrent load
```

Individual keywords, if the form takes a list:

```
Redis
caching
cache-aside
read-through
Spring Boot
Spring Cache
benchmark
performance measurement
concurrent load
```

---

## Resource type

```
Dataset
```

---

## License

```
Creative Commons Attribution 4.0 International (CC BY 4.0)
```

> Scripts in `scripts/` are additionally available under the MIT License.

---

## Authors

| Field | Value |
|---|---|
| Given name | `Yishun` |
| Family name | `Ren` |
| Affiliation | *(leave blank)* |
| ORCID | *(leave blank unless you have one)* |

---

## Language

```
English
```

---

## Version / Publication date

| Field | Value |
|---|---|
| Version | `1.0.0` |
| Publication date | `2026-09-28` |

---

## Related identifiers

| Relation | Identifier |
|---|---|
| Is supplement to / Is identical to | the GitHub repository URL (see below) |
| Is documented by | `README.md` and `docs/DATASET.md` in this repository |

---

## GitHub repository settings

| Field | Value |
|---|---|
| Repository name | `redis-cache-strategy-benchmark` |
| Description | `Controlled benchmark of Cache-Aside vs. framework-managed Read-Through caching in Spring Boot with Redis and MySQL: 30 runs, 11.3M request records.` |
| Topics | `redis` `caching` `cache-aside` `read-through` `spring-boot` `spring-cache` `benchmark` `performance` `dataset` |

---

## Release assets

Attach to the GitHub release **and** upload to the deposit record:

| File | Size | Contents |
|---|---|---|
| `formal-30runs-<date>.tar.gz` | 66 MB | Full dataset: 30 JTL files (770 MB uncompressed, 11,325,558 records), probe snapshots, summary tables, statistical analysis |

> Keep large artifacts out of Git history; attach them to the release instead.
> Note that GitHub-to-Zenodo automatic archiving captures the repository contents only,
> not release assets, so upload the archive to the deposit record manually if you want
> it included there.

---

## Assigned identifiers

| Field | Value |
|---|---|
| Repository | https://github.com/rys888/redis-cache-strategy-benchmark |
| DOI | 10.5281/zenodo.23011850 |

Both `CITATION.cff` and `README.md` already carry this DOI.
