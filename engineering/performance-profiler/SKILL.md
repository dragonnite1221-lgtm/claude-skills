---
name: "performance-profiler"
description: "Find and fix performance bottlenecks in Node.js, Python, and Go apps with a measure-first discipline. performance_profiler.py scans a project directory for risk indicators — dependency counts, bundle-like artifacts and build dirs, and large files over a --large-file-threshold-kb — in text or --json. references/profiling-recipes.md gives the real profiling commands: clinic.js/0x flamegraphs and heap snapshots for Node, py-spy/cProfile/memory_profiler for Python, pprof for Go, plus EXPLAIN ANALYZE and k6/Artillery load tests. Use when an app is slow, P99 exceeds SLA, memory grows (suspected leak), bundle size jumped, or before a traffic spike — e.g. 'why is this endpoint slow', 'profile this service', 'find the memory leak', or 'load test before launch'."
---

# Performance Profiler

Systematic performance work for Node.js, Python, and Go: scan for risk indicators, then
profile, optimize, and re-measure. Always measure before and after.

## Tool

| Tool | Purpose |
|------|---------|
| `scripts/performance_profiler.py` | Scan a project for risk indicators: dependency counts, bundle/build artifacts, large files |

```bash
# Scan for performance risk indicators (text).
python3 scripts/performance_profiler.py /path/to/project

# JSON output for CI integration.
python3 scripts/performance_profiler.py /path/to/project --json

# Flag files larger than a custom threshold (default 512 KB).
python3 scripts/performance_profiler.py /path/to/project --large-file-threshold-kb 256
```

The scanner surfaces *candidates*; it does not profile running code. Use it to point
profiling effort, then run the real tools from
[profiling-recipes.md](references/profiling-recipes.md).

## Golden rule: measure first

Establish a baseline before touching anything — P50/P95/P99 latency, RPS, error rate,
memory. Then: **profile → confirm the bottleneck → fix one thing → re-measure → verify the
delta.** Never optimize on a hunch; you will optimize the wrong thing.

## Profiling recipes

Full commands live in [profiling-recipes.md](references/profiling-recipes.md):

- **Node.js** — clinic.js / 0x CPU flamegraphs, heap snapshots & leak detection, event-loop blocking, autocannon load.
- **Python** — py-spy flamegraphs (no code change), cProfile function-level, memory_profiler line-by-line.
- **Go** — pprof CPU/heap/block profiles.
- **Database** — EXPLAIN ANALYZE, slow query log, N+1 detection.
- **Load testing** — k6 and Artillery scenarios with ramp-up.

## Optimization checklist (quick wins first)

**Database:** missing indexes on WHERE/ORDER BY; N+1 queries (count queries/request);
`SELECT *` when 2-3 columns suffice; unbounded queries (no LIMIT); per-request connections
(no pool).
**Node.js:** sync I/O (`fs.readFileSync`) in hot path; `JSON.parse/stringify` of large
objects in a loop; uncached expensive computations; no gzip/brotli; deps required inside
request handlers.
**Bundle:** Moment.js → dayjs/date-fns; full Lodash → per-function imports; static imports
of heavy components → dynamic; unoptimized images; no route code-splitting.
**API:** no pagination on lists; no `Cache-Control`; serial `await`s that could be
`Promise.all`; fetching related data in a loop instead of a JOIN.

## Document the win

Record baseline and result in the PR — the contrast motivates the team and proves the fix.

```markdown
## Performance: <what you fixed> (PROJ-123)
### Root cause: <what the profiler revealed>
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| P95 latency | 1,240ms | 120ms | -90% |
| RPS @ 50 VUs | 42 | 380 | +804% |
| DB queries/req | 23 (N+1) | 1 | -96% |
### Verification: <link to k6 output / flamegraph>
```

## Common pitfalls

- Optimizing without measuring; testing against dev-sized data instead of production volumes.
- Watching P50 while P99 is catastrophic.
- Optimizing before correctness; skipping the re-measure that proves the fix.
- Load-testing production instead of a production-sized staging environment.

## Reference

- [profiling-recipes.md](references/profiling-recipes.md) — copy-paste profiling commands for Node.js, Python, Go, databases, and load tests
