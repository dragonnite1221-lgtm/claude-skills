---
name: "incident-commander"
description: "Run technology incidents end to end: classify severity (SEV1–SEV4) from impact/urgency and emit escalation paths, reconstruct a chronological timeline from scattered timestamped events with phase detection and gap analysis, and generate blameless Post-Incident Reviews using 5 Whys, Fishbone, Timeline, or Bow-Tie RCA. Six stdlib-only Python tools read JSON (file or stdin) and output text/JSON/markdown. Use when triaging or commanding a live incident, deciding a severity level, building an incident timeline from logs, drafting stakeholder/exec/customer comms, or writing a postmortem/PIR — e.g. 'classify this incident', 'reconstruct the timeline', 'generate a postmortem'."
---

# Incident Commander

A complete incident-response toolkit covering detection → triage → timeline → resolution → post-incident review, implementing SRE/DevOps practices for severity classification, timeline reconstruction, and root-cause analysis.

## Tools

All scripts live in `scripts/`, use only the Python standard library, read JSON from a file argument or stdin, and support `--format {text,json,markdown}`.

| Tool | Purpose |
|------|---------|
| `incident_classifier.py` | Classify an incident, recommend response team and initial actions, emit severity-based comms. `--input/-i`, `--format/-f {json,text}`, `--interactive`, `--output/-o`. |
| `severity_classifier.py` | Classify SEV level and generate escalation paths. Positional `data_file` (or stdin), `--format {text,json,markdown}`. |
| `timeline_reconstructor.py` | Build a chronological timeline from timestamped events. `--input/-i`, `--detect-phases`, `--gap-analysis`, `--min-events`, `--format {json,text,markdown}`. |
| `incident_timeline_builder.py` | Structured timeline with phase detection + communication templates. Positional `data_file`, `--format`. |
| `pir_generator.py` | Post-Incident Review with RCA + action items. `--incident/-i`, `--timeline/-t`, `--rca-method {five_whys,fishbone,timeline,bow_tie}`, `--template-type {comprehensive,standard,brief}`, `--action-items`. |
| `postmortem_generator.py` | Postmortem report with 5-Whys analysis. Positional `data_file`, `--format`. |

Sample inputs ship in `assets/` (`sample_incident_data.json`, `sample_timeline_events.json`, `sample_incident_pir_data.json`, `sample_incident_classification.json`, plus `simple_*` variants).

## Workflow

Run the tools in incident order; fix inputs and re-run any step that errors before moving on.

```bash
# 1a. Quick severity classification from a flat description (stdin)
echo '{"description":"DB connection timeouts, 500s","affected_users":"80%","business_impact":"high"}' \
  | python3 scripts/incident_classifier.py --format text
# 1b. Severity + escalation path from a structured incident file ({"incident": {...}})
python3 scripts/severity_classifier.py assets/sample_incident_data.json --format markdown

# 2. Reconstruct the timeline from collected events (markdown for the doc)
python3 scripts/timeline_reconstructor.py --input assets/sample_timeline_events.json \
  --detect-phases --gap-analysis --format markdown --output timeline.md

# 3. After resolution, generate the PIR / postmortem
python3 scripts/pir_generator.py --incident assets/sample_incident_pir_data.json \
  --timeline timeline.md --rca-method fishbone --action-items --output pir.md
python3 scripts/postmortem_generator.py assets/sample_incident_pir_data.json --format markdown
```

Input JSON shapes are documented in each tool's `--help`.

## Severity model (quick reference)

| SEV | Definition | IC assignment | Comms cadence |
|-----|------------|---------------|---------------|
| SEV1 | Complete outage / data loss / security breach | within 5 min, exec notify 15 min | every 15 min |
| SEV2 | Major degradation (>25% users) | within 30 min | every 30 min |
| SEV3 | Minor, workaround available (<25% users) | response in 2 hrs (biz hrs) | key milestones |
| SEV4 | Cosmetic / no user impact | 1–2 business days | standard cycle |

Full characteristics, response requirements, and the impact×urgency matrix: [incident_severity_matrix.md](references/incident_severity_matrix.md) and [incident-response-framework.md](references/incident-response-framework.md).

## Incident Commander role

The IC owns command-and-control (resource allocation, decisions), acts as the communication hub (shields responders, manages external comms), drives process and documentation, and ensures a blameless post-incident review happens. For SEV1/2 the IC has full authority and biases toward action — document decisions for later review. Decision-making framework and stakeholder management detail: [incident-response-framework.md](references/incident-response-framework.md).

## Reference documentation

| Reference | Use for |
|-----------|---------|
| [incident_severity_matrix.md](references/incident_severity_matrix.md) | SEV1–SEV4 characteristics, impact/urgency scoring |
| [incident-response-framework.md](references/incident-response-framework.md) | IC role, decision-making, stakeholder management, runbook framework |
| [communication_templates.md](references/communication_templates.md) | Initial notification, exec summary, customer/status-page templates and cadence-by-stakeholder |
| [rca_frameworks_guide.md](references/rca_frameworks_guide.md) | 5 Whys, Fishbone, Timeline, Bow-Tie applied to PIRs |
| [sla-management-guide.md](references/sla-management-guide.md) | SLA targets, time-to-detect/engage/resolve tracking |
| [reference-information.md](references/reference-information.md) | Tooling integration, escalation contacts, supplementary detail |

Runbook and report scaffolds: `assets/runbook_template.md`, `assets/incident_report_template.md`.

## Best practices

- **During response:** stay decisive with incomplete information; prefer rollbacks to risky fixes; validate before declaring resolution; document actions and rationale as they happen.
- **Post-incident:** keep it blameless (focus on system failures, not people); assign action items with specific owners and due dates; share PIRs broadly and feed lessons back into runbooks.
- **Comms:** clear, jargon-free, regular updates even when there is no new information; manage stakeholder expectations proactively.
