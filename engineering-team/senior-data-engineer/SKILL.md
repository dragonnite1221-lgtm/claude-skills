---
name: "senior-data-engineer"
description: Data engineering skill for building scalable data pipelines, ETL/ELT systems, and data infrastructure. Expertise in Python, SQL, Spark, Airflow, dbt, Kafka, and modern data stack. Includes data modeling, pipeline orchestration, data quality, and DataOps. Use when designing data architectures, building data pipelines, optimizing data workflows, implementing data governance, or troubleshooting data issues.
---

# Senior Data Engineer

Production-grade data engineering skill for building scalable, reliable data systems.

## Table of Contents

1. [Quick Start](#quick-start)
2. [Workflows](#workflows)
3. [Architecture Decision Framework](#architecture-decision-framework)
4. [Tech Stack](#tech-stack)
5. [Reference Documentation](#reference-documentation)
6. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Core Tools

```bash
# Generate pipeline orchestration config
python scripts/pipeline_orchestrator.py generate \
  --type airflow \
  --source postgres \
  --destination snowflake \
  --schedule "0 5 * * *"

# Validate data quality
python scripts/data_quality_validator.py validate \
  --input data/sales.parquet \
  --schema schemas/sales.json \
  --checks freshness,completeness,uniqueness

# Optimize ETL performance
python scripts/etl_performance_optimizer.py analyze \
  --query queries/daily_aggregation.sql \
  --engine spark \
  --recommend
```

---

## Workflows

Full step-by-step instructions with code live in `references/workflows.md`. Summaries:

### Workflow 1: Building a Batch ETL Pipeline

PostgreSQL → dbt → Snowflake, incremental by watermark column.

1. Document source schema (`information_schema.columns` inventory)
2. Generate extraction config — `pipeline_orchestrator.py generate --mode incremental --watermark updated_at`
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

---

## Architecture Decision Framework

### Batch vs Streaming

```
Is real-time insight required?
├── Yes → Use streaming
│   └── Is exactly-once semantics needed?
│       ├── Yes → Kafka + Flink/Spark Structured Streaming
│       └── No → Kafka + consumer groups
└── No → Use batch
    └── Is data volume > 1TB daily?
        ├── Yes → Spark/Databricks
        └── No → dbt + warehouse compute
```

Batch is cheaper and easier to reprocess; choose streaming only when latency
in seconds-to-minutes genuinely changes a decision downstream.

### Lambda vs Kappa Architecture

**When to choose Lambda:**
- Need to train ML models on historical data
- Complex batch transformations not feasible in streaming
- Existing batch infrastructure

**When to choose Kappa:**
- Event-sourced architecture
- All processing can be expressed as stream operations
- Starting fresh without legacy systems

### Data Warehouse vs Data Lakehouse

**When to choose a warehouse (Snowflake/BigQuery):** BI and SQL analytics
dominate, mature BI tooling matters, schema-on-write is acceptable.

**When to choose a lakehouse (Delta/Iceberg):** ML workloads and unstructured
data, open storage formats for cost control, schema-on-read flexibility.

---

## Tech Stack

| Category | Technologies |
|----------|--------------|
| **Languages** | Python, SQL, Scala |
| **Orchestration** | Airflow, Prefect, Dagster |
| **Transformation** | dbt, Spark, Flink |
| **Streaming** | Kafka, Kinesis, Pub/Sub |
| **Storage** | S3, GCS, Delta Lake, Iceberg |
| **Warehouses** | Snowflake, BigQuery, Redshift, Databricks |
| **Quality** | Great Expectations, dbt tests, Monte Carlo |
| **Monitoring** | Prometheus, Grafana, Datadog |

---

## Reference Documentation

### 1. Data Pipeline Architecture
See `references/data_pipeline_architecture.md` for:
- Lambda vs Kappa architecture patterns
- Batch processing with Spark and Airflow
- Stream processing with Kafka and Flink
- Exactly-once semantics implementation
- Error handling and dead letter queues

### 2. Data Modeling Patterns
See `references/data_modeling_patterns.md` for:
- Dimensional modeling (Star/Snowflake)
- Slowly Changing Dimensions (SCD Types 1-6)
- Data Vault modeling
- dbt best practices
- Partitioning and clustering

### 3. DataOps Best Practices
See `references/dataops_best_practices.md` for:
- Data testing frameworks
- Data contracts and schema validation
- CI/CD for data pipelines
- Observability and lineage
- Incident response

---

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
