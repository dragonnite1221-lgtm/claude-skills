---
title: "Product Manager Toolkit — Agent Skill for Product Teams"
description: "Product management toolkit covering RICE prioritization, customer-interview synthesis, PRD authoring, discovery frameworks, and go-to-market. Runs. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Product Manager Toolkit

<div class="page-meta" markdown>
<span class="meta-badge">:material-lightbulb-outline: Product</span>
<span class="meta-badge">:material-identifier: `product-manager-toolkit`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/product-team/product-manager-toolkit/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install product-skills</code>
</div>


Tools and frameworks for product management from discovery to delivery. Two stdlib-only
CLI tools plus PRD templates and framework references.

## Quick Start

```bash
# Feature prioritization (create sample data, then score with team capacity)
python scripts/rice_prioritizer.py sample
python scripts/rice_prioritizer.py sample_features.csv --capacity 15

# Interview analysis
python scripts/customer_interview_analyzer.py interview_transcript.txt
```

For PRDs: pick a template from `references/prd_templates.md`, fill it from discovery work,
review with engineering for feasibility, and version-control it.

## Tools

### rice_prioritizer.py

Scores features by RICE — `(Reach x Impact x Confidence) / Effort` — with portfolio
balance analysis (quick wins vs big bets) and quarterly roadmap generation by capacity.

```bash
python scripts/rice_prioritizer.py sample                       # write sample_features.csv
python scripts/rice_prioritizer.py features.csv                 # default 10 person-month capacity
python scripts/rice_prioritizer.py features.csv --capacity 20   # custom quarterly capacity
python scripts/rice_prioritizer.py features.csv --output json   # json | csv | text (default)
```

CSV input columns: `name,reach,impact,confidence,effort,description`. `impact` accepts
massive/high/medium/low/minimal; `effort` accepts t-shirt sizes (s/m/l/xl). See
`assets/rice_input_template.csv` and `references/frameworks.md` for scoring guidelines.

### customer_interview_analyzer.py

Extracts pain points (with severity), feature requests, jobs-to-be-done patterns,
per-section sentiment, themes, notable quotes, and competitor mentions from a transcript.

```bash
python scripts/customer_interview_analyzer.py interview.txt           # human-readable
python scripts/customer_interview_analyzer.py interview.txt --json    # JSON for aggregation
```

## Workflows

### Feature prioritization

Gather requests (customer feedback, sales blockers, tech debt, strategic initiatives) →
score with `rice_prioritizer.py` → analyze the portfolio (quick wins vs big bets, effort
concentration, strategic-alignment gaps) → generate a quarterly roadmap → validate before
finalizing:

- [ ] Compare top priorities against strategic goals
- [ ] Run sensitivity analysis (what if estimates are wrong by 2x?)
- [ ] Review with stakeholders for blind spots
- [ ] Check for missing dependencies between features
- [ ] Validate effort estimates with engineering

Then execute: track actual vs estimated effort and revisit RICE inputs quarterly.

### Customer discovery

Plan research questions and target segments → recruit 5-8 participants per segment (mix
power users and churned) → conduct semi-structured interviews focused on problems, not
solutions → analyze with `customer_interview_analyzer.py` → synthesize (group pain points,
3+ mentions = pattern, map to an Opportunity Solution Tree, prioritize by frequency and
severity) → validate before building:

- [ ] Create solution hypotheses (see `references/frameworks.md`)
- [ ] Test with low-fidelity prototypes
- [ ] Measure actual behavior vs stated preference
- [ ] Iterate and document learnings

### PRD development

Choose a template, draft, review, refine, approve, track.

| Template | Use case | Timeline |
|----------|----------|----------|
| Standard PRD | Complex features, cross-team | 6-8 weeks |
| One-Page PRD | Simple features, single team | 2-4 weeks |
| Feature Brief | Exploration phase | 1 week |
| Agile Epic | Sprint-based delivery | Ongoing |

Draft problem-first with success metrics and explicit out-of-scope; review across
engineering (feasibility), design (UX gaps), sales (market), and support (operational
impact); document trade-offs; then track actual metrics vs targets after launch.

## Integration

JSON output integrates with most PM tooling — analytics (Amplitude, Mixpanel),
roadmapping (ProductBoard, Aha!), trackers (Jira, Linear, GitHub), and research
(Dovetail, Maze). Example: `python scripts/rice_prioritizer.py features.csv --output json > priorities.json`.

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| **Solution-first** — features before understanding problems | Start every PRD with a problem statement |
| **Analysis paralysis** — over-researching without shipping | Time-box research phases |
| **Feature factory** — shipping without measuring impact | Define success metrics before building |
| **Ignoring tech debt** — no time for platform health | Reserve ~20% capacity for maintenance |
| **Stakeholder surprise** — not communicating early | Weekly async updates, monthly demos |
| **Metric theater** — optimizing vanity metrics | Tie metrics to user value delivered |

## References

- `references/frameworks.md` — RICE, MoSCoW, Kano, JTBD scoring and interview scripts
- `references/prd_templates.md` — PRD templates per context
- `references/input-output-examples.md` — worked tool input/output examples
- `assets/prd_template.md`, `assets/rice_input_template.csv` — ready-to-use templates
