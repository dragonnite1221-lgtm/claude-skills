---
name: "migration-architect"
description: >
  Plan zero-downtime system, database, and infrastructure migrations from a JSON migration
  spec. migration_planner.py generates a phased plan with validation gates, risk assessment,
  and timeline; compatibility_checker.py diffs before/after database schemas or API specs to
  flag breaking and potentially-breaking changes; rollback_generator.py turns a plan into a
  step-by-step rollback runbook. Applies expand-contract, strangler-fig, dual-write, CDC,
  blue-green, and canary patterns. Use when the user wants to plan a migration, check schema or
  API backward compatibility, assess migration risk, or generate a rollback runbook — e.g.
  "plan a zero-downtime migration", "is this schema change breaking?", "migrate Postgres to the
  cloud", or "generate a rollback plan".
license: MIT
metadata:
  tier: POWERFUL
  category: engineering
---

# Migration Architect

Plan, validate, and de-risk complex system, database, and infrastructure migrations with
minimal downtime. Three stdlib-only tools turn a JSON migration spec into a phased plan, a
compatibility report, and a rollback runbook.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/migration_planner.py` | JSON spec → phased migration plan (gates, risks, timeline) |
| `scripts/compatibility_checker.py` | Diff before/after database schemas or API specs for breaking changes |
| `scripts/rollback_generator.py` | Migration plan → step-by-step rollback runbook |

## Workflow

Run the gates in order. On a failure or a flagged breaking change, fix the spec/schema and
re-run that step before moving on.

```bash
# 1. Validate the migration spec, then generate a phased plan.
python3 scripts/migration_planner.py -i assets/sample_database_migration.json --validate
python3 scripts/migration_planner.py -i assets/sample_database_migration.json \
  -o migration_plan.json --format both

# 2. Check schema (or API) compatibility before executing.
python3 scripts/compatibility_checker.py \
  --before assets/database_schema_before.json \
  --after  assets/database_schema_after.json \
  --type database --format text
#   --type api compares OpenAPI/endpoint specs instead.

# 3. Generate the rollback runbook from the plan produced in step 1.
python3 scripts/rollback_generator.py -i migration_plan.json -o rollback_runbook.json --format both
```

All tools accept `--format json|text|both`. The migration spec is JSON with `type`
(`database`/`service`/`infrastructure`), `pattern`, `source`, `target`, `constraints`
(max downtime, data volume, dependencies, compliance, special requirements), and per-resource
detail. See `assets/sample_database_migration.json` and `assets/sample_service_migration.json`
for complete examples, and `expected_outputs/` for reference plan/report/runbook output.

## Choosing a Migration Pattern

| Situation | Pattern |
|-----------|---------|
| Evolve a schema with no downtime | **Expand-contract** — add new, dual-write, backfill, then drop old |
| Replace a legacy service incrementally | **Strangler fig** — route through a gateway, replace piece by piece |
| Move large data live | **CDC / dual-write** — stream changes to the target, cut over when consistent |
| De-risk a service cutover | **Blue-green** or **canary** — keep the old version, shift traffic gradually |
| Validate correctness before cutover | **Parallel run** — run both, compare outputs (shadow traffic) |

Full pattern catalog, zero-downtime techniques, and data-reconciliation strategies live in
references (below). Always design every step with a tested rollback before executing.

## Validation & Reconciliation

Before cutover, confirm data parity with row-count comparison, checksums/hashing on critical
subsets (sample large datasets), and business-logic checks (compare aggregate query results on
both systems). Detect deltas with `NOT EXISTS` anti-join queries between source and target, and
repair with idempotent correction scripts that log every action. Details:
[data_reconciliation_strategies.md](references/data_reconciliation_strategies.md).

## References

| File | Contents |
|------|----------|
| [migration_patterns_catalog.md](references/migration_patterns_catalog.md) | Database/service/infrastructure patterns with trade-offs |
| [zero_downtime_techniques.md](references/zero_downtime_techniques.md) | Expand-contract, feature flags, circuit breakers, traffic routing |
| [data_reconciliation_strategies.md](references/data_reconciliation_strategies.md) | Row-count, checksum, and business-logic validation; delta detection |
