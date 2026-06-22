---
title: "Observability Designer — Agent Skill for Codex & OpenClaw"
description: "Design production observability — SLI/SLO frameworks, dashboards, and alert tuning — from a service-description JSON. slo_designer.py turns service. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Observability Designer

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `observability-designer`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/observability-designer/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Design SLI/SLO frameworks, dashboards, and alerting for production systems. Three
stdlib-only tools take a service-description JSON (or CLI flags) and produce frameworks,
Grafana dashboards, and optimized alert configs.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/slo_designer.py` | Service description → SLIs, SLO targets, error budgets, burn-rate alerts, SLA recommendations |
| `scripts/dashboard_generator.py` | Service description → Grafana-compatible dashboard (golden signals, RED/USE, role views) |
| `scripts/alert_optimizer.py` | Existing alert config → noise/duplicate/coverage analysis + optimized config |

## Workflow

Design SLOs first (they set dashboard thresholds and alert targets), then generate the
dashboard, then optimize alerts. After optimizing alerts, re-run `--analyze-only` on the
new config to confirm the warnings cleared before shipping.

```bash
# 1. SLO framework from a service definition (or pass --service-type/--criticality flags).
python3 scripts/slo_designer.py -i assets/sample_service_api.json -o slo_framework.json
python3 scripts/slo_designer.py --service-type api --criticality high --user-facing true --summary-only

# 2. Grafana dashboard for the same service, tuned for a role.
python3 scripts/dashboard_generator.py -i assets/sample_service_api.json \
  --format grafana --role sre -o dashboard.json --doc-output dashboard.md

# 3. Analyze an existing alert config, then emit the optimized version.
python3 scripts/alert_optimizer.py -i assets/sample_alerts.json --analyze-only
python3 scripts/alert_optimizer.py -i assets/sample_alerts.json -o optimized_alerts.json
python3 scripts/alert_optimizer.py -i assets/sample_alerts.json --report report.html --format html
```

Service-type choices: `api|web|database|queue|batch|ml`; criticality `critical|high|medium|low`;
dashboard roles `sre|developer|executive|ops`. Sample inputs are in `assets/`
(`sample_service_api.json`, `sample_service_web.json`, `sample_alerts.json`); reference
outputs are in `expected_outputs/` (`sample_slo_framework.json`, `sample_dashboard.json`).

## Design principles

**SLI/SLO** — pick SLIs that track user experience (availability, latency, correctness),
set SLO targets, derive an error budget, and alert on multi-window burn rate rather than
raw thresholds. See [slo_cookbook.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/observability-designer/references/slo_cookbook.md).

**Dashboards** — golden signals (latency, traffic, errors, saturation) for request
services; RED (rate/errors/duration) for services, USE (utilization/saturation/errors) for
resources. Keep to ~7±2 panels per screen, with overview → service → instance drill-down
and SLO reference lines. See [dashboard_best_practices.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/observability-designer/references/dashboard_best_practices.md).

**Alerts** — every alert must be actionable. Favor precision over recall, use hysteresis
(separate firing/resolving thresholds), group related alerts, and suppress dependents
during known outages. See [alert_design_patterns.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/observability-designer/references/alert_design_patterns.md).

## References

| File | Contents |
|------|----------|
| [slo_cookbook.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/observability-designer/references/slo_cookbook.md) | SLI selection, SLO targets, error budgets, burn-rate alerting |
| [dashboard_best_practices.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/observability-designer/references/dashboard_best_practices.md) | Golden signals, RED/USE, layout, visualization choices |
| [alert_design_patterns.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/observability-designer/references/alert_design_patterns.md) | Severity, actionability, fatigue prevention, threshold selection |
