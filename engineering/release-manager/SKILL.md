---
name: "release-manager"
description: "Manages software release workflows and produces CHANGELOG.md entries, semantic-version recommendations, release-readiness plans, deployment checklists, and rollback/hotfix procedures. Use when planning a release, analyzing conventional commits, coordinating a release branch or git tag, or preparing deployment and recovery artifacts."
---

# Release Manager

Use this skill to turn repository evidence into a reviewable release package.
Default to planning and artifact generation. Do not create branches, tags,
deployments, or external announcements unless the user explicitly authorizes
those state-changing actions.

## Choose the workflow

1. If the user only needs release notes, run the changelog generator.
2. If the next version is unknown, run the version bumper on commits since the
   last release, then generate the changelog with the recommended version.
3. If release readiness or coordination is requested, collect the release-plan
   JSON and run the release planner with checklist and rollback output.
4. For an urgent production correction, follow
   [hotfix procedures](references/hotfix-procedures.md).
5. For workflow selection:
   - Trunk-based: frequent deploys, short-lived branches, feature flags.
   - GitHub Flow: lightweight PR-based release from `main`.
   - Git Flow: scheduled releases with a maintained `develop` branch.
   - Monorepo: calculate affected-package versions independently and record
     cross-package compatibility in the plan.

See [release workflow comparison](references/release-workflow-comparison.md)
for detailed tradeoffs. See
[conventional commits guide](references/conventional-commits-guide.md) for the
accepted commit grammar and bump rules.

## Inputs to establish

- Current version and last release tag.
- Commit range and whether conventional commits are enforced.
- Release scope: single package, coordinated packages, or whole repository.
- Required CI, coverage, security, migration, and approval gates.
- Deployment environment, rollout strategy, observability, and rollback owner.
- Whether the user authorizes Git writes or deployment actions.

When an input is unavailable, state the assumption in the generated plan. Never
invent a passing gate, approval, deployment result, or rollback verification.

## Script usage

Run from the repository root. The scripts analyze files/stdin and write only to
an explicit `--output` path.

Generate `CHANGELOG.md` content from a git-log export:

```bash
python engineering/release-manager/changelog_generator.py \
  --input commits.txt --input-format git-log --version 2.4.0 \
  --format markdown --summary --output CHANGELOG.generated.md
```

Expected output: grouped Added/Fixed/Changed/Breaking sections plus summary
counts in `CHANGELOG.generated.md`. Review before merging into the canonical
changelog.

Recommend a semver bump and emit proposed commands without executing them:

```bash
python engineering/release-manager/version_bumper.py \
  --current-version 2.3.1 --input commits.txt --input-format git-log \
  --analysis --include-commands --output-format json \
  --output version-recommendation.json
```

Expected output: current/recommended version, bump reason, commit analysis, and
optional command strings in `version-recommendation.json`.

Assess readiness and produce coordination artifacts:

```bash
python engineering/release-manager/release_planner.py \
  --input release-plan.json --output-format markdown \
  --include-checklist --include-communication --include-rollback \
  --min-coverage 85 --output release-readiness.md
```

Expected output: PASS/BLOCKED gate summary, deployment checklist, communication
plan, and rollback runbook. A blocked gate remains blocking until real evidence
is supplied.

## Release decision gates

Require evidence for the gates that apply:

- Tests, static analysis, dependency/security scans, and required coverage.
- Breaking-change migration guidance and API/schema compatibility.
- Database migration rehearsal and backward-compatible rollback.
- Artifact provenance, version consistency, and changelog completeness.
- Deployment health metrics, alert ownership, and rollback trigger thresholds.
- Product, engineering, QA, security, legal, or compliance approvals.

Classify each gate as `pass`, `blocked`, or `not_applicable`, with evidence and
an owner. Do not turn `unknown` into `pass`.

## Deliverable

Return a compact release packet containing:

1. Recommended version and reasoning.
2. Changelog draft and breaking-change notes.
3. Gate table with evidence, owner, and status.
4. Ordered deployment plan and validation checkpoints.
5. Rollback triggers, steps, and recovery verification.
6. Exact commands proposed for any authorized Git/release action.
7. Remaining blockers and the next responsible party.

Keep generated artifacts separate from canonical files until reviewed. If the
user authorizes execution, re-check the current branch, working tree, CI state,
and target environment immediately before each irreversible action.
