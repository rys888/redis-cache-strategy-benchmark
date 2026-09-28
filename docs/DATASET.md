# Dataset Documentation

Field-level reference for the Redis cache strategy benchmark dataset.

---

## 1. Files and roles

| Path | Rows | Role |
|---|---|---|
| `data/run_level/run_level.csv` | 30 | **Primary analysis table.** One row per independent run. |
| `data/run_level/descriptive_stats.csv` | 6 | Aggregates by strategy × concurrency. |
| `data/run_level/runs_index.csv` | 30 | Run index plus environment and validity metadata. |
| `data/raw/meta/*.stats.json` | 30 | Application probe counters captured after each run. |
| `data/raw/meta/*.jtlstats` | 30 | Parsed window statistics per run. |
| `analysis/*` | — | Statistical outputs and figures. |
| `experiment-plan/cache_experiment.jmx` | — | JMeter test plan. |
| `experiment-plan/id_pool.csv` | 20 | The fixed set of primary IDs used by every run. |

---

## 2. `run_level.csv` — primary table

**Unit of observation: one independent run.** Do not treat individual requests as observations.

| Column | Type | Description |
|---|---|---|
| `run_id` | string | Run identifier, e.g. `r1_cache-aside_c25_20260928-102107` |
| `strategy` | categorical | `cache-aside` or `read-through` |
| `concurrency` | integer | 25, 50 or 100 (JMeter thread count) |
| `repetition` | integer | 1–5 |
| `order_in_block` | integer | Position within the randomized block (1–6) |
| `sample_count` | integer | Requests completed within the 60 s measurement window |
| `dropped_samples` | integer | Samples excluded as ramp-up |
| `AvgRT` | float | Mean response time, ms |
| `MedianRT` | float | Median response time, ms |
| `P95` | float | 95th percentile response time, ms |
| `Throughput` | float | Requests per second, computed as `sample_count / 60` |
| `ErrorRate` | float | Fraction of failed requests (0.0 in all runs) |
| `errors` | integer | Failed request count (0 in all runs) |
| `avg_response_bytes` | float | Mean response body size, bytes |
| `window_seconds` | float | Observed span of the measurement window (quality indicator) |

### Notes on derived fields

**Throughput** uses a fixed 60 s denominator rather than the observed span. The observed span is
59.91–59.97 s; using it directly would inflate throughput by roughly 0.1%. The observed value is
retained separately in `window_seconds`.

**P95 quantization.** The source `elapsed` field is integer milliseconds. P95 values are therefore
multiples of 1 ms, and two cells show zero within-cell variance (see README §8).

---

## 3. `runs_index.csv` — environment and validity metadata

| Column | Description |
|---|---|
| `run_id` | Run identifier (joins to `run_level.csv`) |
| `strategy`, `concurrency`, `repetition`, `order_in_block` | Design factors |
| `ramp_s`, `duration_s`, `total_duration_s` | 15 / 60 / 75 |
| `start_time`, `end_time` | Wall-clock timestamps |
| `redis_hits`, `redis_misses` | `keyspace_hits` / `keyspace_misses` after the run |
| `keys_all_exist` | `True` if all 20 cache keys were present at verification |
| `min_pttl_ms` | Minimum remaining TTL observed, ms |
| `dbsize` | Redis `DBSIZE` after the run (20) |
| `used_memory_human` | Redis `used_memory_human` |
| `load_avg` | 1/5/15-minute load average of the application host |
| `jtl_file` | Corresponding raw JTL filename |

---

## 4. `meta/*.stats.json` — application probe counters

Captured immediately after each run, before any reset.

```json
{
  "dbLoadCount": 0,
  "readThroughMethodInvocations": 0,
  "cacheAsideRedisHits": 0,
  "cacheAsideRedisMisses": 0,
  "cacheName": "laureate",
  "keyPrefix": "laureate:",
  "ttlSeconds": 300
}
```

| Counter | Meaning | Expected in this dataset |
|---|---|---|
| `dbLoadCount` | Database loads (cache misses that reached the repository) | **0** — proves Hot Cache steady state |
| `readThroughMethodInvocations` | Executions of the `@Cacheable` target method body | **0** — proves hits bypass the method |
| `cacheAsideRedisHits` | Explicit hit counter on the Cache-Aside path | **0** — intentionally disabled during measurement |
| `cacheAsideRedisMisses` | Explicit miss counter on the Cache-Aside path | **0** |

The hit counter is disabled during measurement because it adds an atomic operation to one
strategy's hot path but not the other (see README §4).

---

## 5. `meta/*.jtlstats` — parsed window statistics

Single-line, space-separated:

```
<total_samples> <full_span_s> <window_samples> <window_span_s> <mean_elapsed_ms> <errors> <error_pct>
```

| Field | Description |
|---|---|
| `total_samples` | Samples in the whole JTL file |
| `full_span_s` | Span of the whole file, seconds (≈74 s including ramp-up) |
| `window_samples` | Samples inside the 60 s measurement window |
| `window_span_s` | Observed span of the measurement window (≈59.9 s) |
| `mean_elapsed_ms` | Mean response time within the window |
| `errors` | Failed samples within the window |
| `error_pct` | Error percentage within the window |

---

## 6. Raw request-level data (JTL)

Format: comma-separated, one row per request.

```
timeStamp,elapsed,label,responseCode,success,bytes,sentBytes,
grpThreads,allThreads,Latency,Connect
```

| Field | Description |
|---|---|
| `timeStamp` | Epoch milliseconds |
| `elapsed` | Response time, integer ms (includes queueing at the client) |
| `label` | Sampler label (`laureate-get`) |
| `responseCode` | HTTP status (200 for all successful samples) |
| `success` | `true` / `false` |
| `bytes` | Response body size, bytes |
| `sentBytes` | Request size, bytes |
| `Latency` | Time to first byte, ms |
| `Connect` | Connection establishment time, ms (0 in steady state) |
| `grpThreads`, `allThreads` | Active thread counts |

### Obtaining the raw data

The complete JTL set (**30 files, 770 MB, 11,325,558 request records**) is distributed as a
compressed archive alongside tagged releases rather than in Git history, to keep the repository
lightweight.

To use it:

1. Download `formal-30runs-20260928.tar.gz` from the Releases page, the deposit record, or
   the DOI landing page.
2. Extract it. The archive unpacks to `formal-30runs/results/` containing:
   - `jtl/` — 30 files, one per run. Each `<run_id>.jtl` maps to one row of `run_level.csv`
     through the `jtl_file` column of `runs_index.csv`.
   - `meta/` — per-run probe snapshots (identical to `data/raw/meta/` here).
   - `summary/` — analysis-ready tables and the full `analysis/` directory (identical to the
     files committed in this repository).
   - `logs/` — 60 JMeter console logs, already redacted (host identifiers replaced;
     no measurement values altered). Not required for analysis.
3. Verify integrity against the SHA-256 manifest included in the archive.

### Parsing the raw data efficiently

A full JTL set parses in a few seconds:

```python
import glob, pandas as pd

COLS = ["timeStamp", "elapsed", "success", "bytes", "Latency"]
DTYPES = {"timeStamp": "int64", "elapsed": "int32", "success": "category",
          "bytes": "int32", "Latency": "int32"}

frames = [pd.read_csv(f, usecols=COLS, dtype=DTYPES) for f in glob.glob("results/jtl/*.jtl")]
df = pd.concat(frames, ignore_index=True)      # ~0.3 GB in memory for 14M rows
```

Reading all 30 files takes about 2 s serially and under 1 s with 4 worker processes.
Memory footprint stays well under 1 GB.

---

## 7. What the raw data is for

The run-level table answers questions about **run-to-run and condition-level behaviour**.
The request-level data answers questions the run-level table cannot:

| Question | Use |
|---|---|
| Latency distribution shape (skew, multimodality) | raw JTL |
| Tail latency beyond P95 (P99, P99.9) | raw JTL |
| Within-run temporal drift during the 60 s window | raw JTL |
| Per-request correlation and autocorrelation diagnostics | raw JTL |
| Condition-level comparisons and regression | `run_level.csv` |

> **Do not substitute request-level rows for run-level rows in a regression model.**
> Requests within a run share CPU state, cache state and JIT state, and are strongly
> autocorrelated. Treating them as independent observations is pseudoreplication: it drives the
> standard error toward zero and produces spuriously significant results.

---

## 8. Reproducing the dataset

The benchmark requires two hosts (application host and load generator host) on the same private
network. The JMeter test plan is provided in `experiment-plan/`.

Run protocol per repetition block (6 conditions in randomized order):

```bash
# application host
export APP_PROBE_ENABLED=false          # disable the asymmetric hot-path counter
export CONCURRENCY=25
export RAMP_SECONDS=15
export DURATION_SECONDS=60
export REPETITIONS=5

# warm up 20 IDs, verify keys/TTL, reset statistics, run JMeter,
# apply the 7 validity gates, record metadata
```

Each run produces one JTL file, one probe JSON, one window-statistics file, and one row in the
run index. Runs failing any validity gate are excluded.

---

## 9. Integrity

| Item | Value |
|---|---|
| Runs | 30 (all passed validity gates) |
| Requests | 11,325,558 (plus 2,569,821 excluded as ramp-up) |
| Window span | 59.91 – 59.97 s |
| Errors | 0 |
| Database loads during measurement | 0 |
| Cache misses during measurement | 0 |
| Environment fingerprint | SHA-256 manifest available alongside the raw archive |
