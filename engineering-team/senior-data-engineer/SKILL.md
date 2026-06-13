---
name: "senior-data-engineer"
description: Build scalable data pipelines, ETL/ELT systems, and data infrastructure with Python, SQL, Spark, Airflow, dbt, and Kafka. Covers dimensional data modeling, pipeline orchestration, data quality frameworks, and DataOps. Use when designing a data architecture (batch vs streaming, warehouse vs lakehouse), building or scheduling data pipelines, adding data quality checks or data contracts, tuning slow Spark or SQL jobs, or troubleshooting failing DAGs and schema drift.
---

# Senior Data Engineer

Production-grade data engineering skill for building scalable, reliable data systems.

## Quick Start

Three CLI tools ship with this skill. Pick by task:

| Task | Tool |
|------|------|
| Scaffold an Airflow/Prefect/Dagster pipeline | `scripts/pipeline_orchestrator.py` |
| Validate a dataset (CSV/JSON/JSONL) against a schema | `scripts/data_quality_validator.py` |
| Profile a slow SQL query or Spark job | `scripts/etl_performance_optimizer.py` (`analyze-sql` / `analyze-spark`) |

```bash
# Generate pipeline orchestration config (DAG file written to --output)
python scripts/pipeline_orchestrator.py generate \
  --type airflow \
  --source postgres \
  --destination snowflake \
  --schedule "0 5 * * *"

# Validate data quality (exits 1 on error-severity failures — safe for CI gates)
python scripts/data_quality_validator.py validate data/sales.csv \
  --schema schemas/sales.json \
  --json

# Analyze a slow SQL query and get prioritized tuning recommendations
python scripts/etl_performance_optimizer.py analyze-sql queries/daily_aggregation.sql \
  --warehouse snowflake
```

All tools run on the Python standard library. `pipeline_orchestrator.py`
accepts JSON config files everywhere; YAML configs work too when PyYAML is
installed (optional, auto-detected).

## Workflows

Full step-by-step instructions with code live in `references/workflows.md`. Summaries:

### Workflow 1: Building a Batch ETL Pipeline

PostgreSQL → dbt → Snowflake, incremental by watermark column.

1. Document source schema (`information_schema.columns` inventory)
2. Generate extraction config — `pipeline_orchestrator.py generate --mode incremental --tables orders,customers`
3. Create dbt staging + mart models (incremental materialization, `unique_key`, clustering)
4. **Validation gate:** add dbt tests (not_null, unique, relationships) before scheduling
5. Create Airflow DAG wiring extract → transform → test
6. **Validation gate:** run end-to-end with a bounded date range and reconcile row counts against source

### Workflow 2: Implementing Real-Time Streaming

Kafka → Flink/Spark Structured Streaming → data lake sink.

1. Define event schema (Avro/JSON Schema, registered before producers ship)
2. Create Kafka topic with partition/retention sizing
3. Implement streaming job with checkpointing enabled
4. **Validation gate:** handle late data (watermarks) and route bad records to a dead-letter queue
5. Monitor stream health — consumer lag, checkpoint age, throughput

### Workflow 3: Data Quality Framework Setup

Great Expectations + dbt tests + data contracts.

1. Initialize Great Expectations project
2. Create expectation suites for critical tables (completeness, uniqueness, ranges)
3. Add dbt schema tests so quality runs inside the pipeline
4. **Validation gate:** enforce data contracts on schema changes (fail closed on breaking change)
5. Publish a quality dashboard for freshness and failure trends

## Architecture Decisions

Project-specific decision criteria (batch vs streaming decision tree, Lambda
vs Kappa, warehouse vs lakehouse selection) live in
`references/data_pipeline_architecture.md`. Consult it when latency, volume,
or reprocessing requirements make the choice non-obvious.

## Reference Documentation

| Reference | Use for |
|-----------|---------|
| `references/data_pipeline_architecture.md` | Batch/stream patterns, exactly-once semantics, dead letter queues, architecture selection |
| `references/data_modeling_patterns.md` | Star/Snowflake dimensional modeling, SCD Types 1-6, Data Vault, dbt practices, partitioning |
| `references/dataops_best_practices.md` | Data testing, data contracts, CI/CD for pipelines, observability and lineage, incident response |
| `references/workflows.md` | Full step-by-step code for the three workflows above |
| `references/troubleshooting.md` | Complete diagnostics for the failures summarized below |

## Troubleshooting

Quick reference for the most common failures — full diagnostics and code in
`references/troubleshooting.md`:

1. **Airflow DAG timeout** — raise `execution_timeout` in `default_args` and
   switch full reloads to incremental (`WHERE updated_at > '{{ prev_ds }}'`).
2. **Spark job OOM** — increase `spark.executor.memory`, raise
   `spark.sql.shuffle.partitions`, and let large shuffles spill to disk.
3. **Schema drift / stale data** — add dbt source freshness checks and enforce
   data contracts so breaking schema changes fail the pipeline instead of
   silently corrupting downstream models.
