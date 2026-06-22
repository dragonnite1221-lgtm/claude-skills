---
title: "Agent Workflow Designer — Agent Skill for Codex & OpenClaw"
description: "Design multi-agent workflows and generate ready-to-edit JSON skeleton configs for five orchestration patterns — sequential, parallel. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Agent Workflow Designer

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `agent-workflow-designer`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/agent-workflow-designer/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Design production-grade multi-agent workflows with clear pattern choice, handoff contracts, failure handling, and cost/context controls. The scaffolder emits a JSON skeleton you then fill in with concrete agents and prompts.

## When to use

- A single prompt is insufficient for task complexity.
- You need specialist agents with explicit boundaries and handoff contracts.
- You want a deterministic workflow structure before implementation.
- You need validation loops for quality or safety gates.

## Pattern map

Pick the smallest pattern that satisfies the dependency shape and risk profile:

- `sequential` — strict step-by-step dependency chain (research → draft → review).
- `parallel` — fan-out independent subtasks, then fan-in to synthesize.
- `router` — dispatch by intent/type to a handler, with a fallback agent.
- `orchestrator` — a planner coordinates specialists over a DAG of dependencies.
- `evaluator` — a generator runs against an evaluator quality gate in a retry loop.

Detailed templates and tradeoffs: [workflow-patterns.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/agent-workflow-designer/references/workflow-patterns.md).

## Generate a skeleton

`scripts/workflow_scaffolder.py PATTERN [--name NAME] [--output PATH]`. With no
`--output` it prints the JSON to stdout; with `--output` it writes the file
(creating parent dirs).

```bash
# Print a sequential skeleton to stdout
python3 scripts/workflow_scaffolder.py sequential --name content-pipeline

# Write an orchestrator workflow to a file
python3 scripts/workflow_scaffolder.py orchestrator --name incident-triage \
  --output workflows/incident-triage.json

# Other patterns: parallel | router | evaluator
python3 scripts/workflow_scaffolder.py evaluator --name draft-and-grade
```

Each skeleton ships with pattern-appropriate guardrail fields already present —
`retry` (sequential), `timeouts` (parallel), `fallback` (router),
`execution.max_parallel`/`completion_policy` (orchestrator), and
`loop.max_iterations`/`pass_threshold` (evaluator).

## Recommended workflow

1. Select the pattern from the map above.
2. Scaffold the config with `workflow_scaffolder.py`.
3. Replace placeholder agent IDs and define the handoff contract fields on every edge.
4. Confirm retry/timeout and output-validation gates are set per step.
5. Dry-run with small context budgets, inspect intermediate outputs, then scale up.

## Common pitfalls

- Over-orchestrating tasks solvable by one well-structured prompt — start small.
- Missing timeout/retry policies on external-model calls.
- Passing full upstream context instead of targeted artifacts (raises cost and noise).
- Skipping validation of intermediate outputs before fan-in synthesis.
- Ignoring per-step cost accumulation across long-running flows.
