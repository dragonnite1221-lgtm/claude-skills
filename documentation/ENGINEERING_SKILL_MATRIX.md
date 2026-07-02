# Engineering Skill Matrix

This matrix explains why the repository has both `engineering-team/` and
`engineering/`, and which folder to choose when topics overlap.

Do not merge or rename these folders. Folder names are user-facing install
paths and ClawHub/Gemini/Codex compatibility surfaces.

## Folder Boundary

| Folder | Use For | Default User Intent |
|---|---|---|
| `engineering-team/` | Role-oriented delivery skills for people doing engineering work | "Act as a senior frontend/backend/devops/security/data engineer and help me build, review, or operate this system." |
| `engineering/` | Advanced workflow, platform, and agent/tooling skills | "Design the automation, process, platform, MCP server, RAG system, evaluation loop, migration, or reusable engineering workflow." |

## Topic Routing

| Topic | Start With | Related Advanced Skill | Boundary |
|---|---|---|---|
| Architecture | `engineering-team/senior-architect` | `engineering/migration-architect`, `engineering/codebase-onboarding` | Use senior-architect for system design decisions; use advanced skills for migration plans, onboarding systems, or reusable architecture workflows. |
| API design | `engineering-team/senior-backend` | `engineering/api-design-reviewer`, `engineering/api-test-suite-builder` | Use senior-backend to build APIs; use advanced skills to review API contracts or generate test suites. |
| Frontend | `engineering-team/senior-frontend`, `engineering-team/senior-fullstack` | `engineering/performance-profiler`, `engineering/observability-designer` | Use team skills for implementation; use advanced skills for cross-app performance and telemetry programs. |
| QA and testing | `engineering-team/senior-qa`, `engineering-team/playwright-pro`, `engineering-team/tdd-guide` | `engineering/skill-tester`, `engineering/self-eval`, `engineering/api-test-suite-builder` | Use team skills for product tests; use advanced skills to evaluate skills, agents, APIs, or work quality. |
| DevOps and cloud | `engineering-team/senior-devops`, cloud architect skills | `engineering/ci-cd-pipeline-builder`, `engineering/docker-development`, `engineering/helm-chart-builder`, `engineering/terraform-patterns`, `engineering/release-manager` | Use team skills for operational advice; use advanced skills to generate or standardize platform workflows. |
| Security | `engineering-team/senior-security`, `engineering-team/senior-secops`, `engineering-team/cloud-security`, `engineering-team/incident-response` | `engineering/skill-security-auditor`, `engineering/dependency-auditor`, `engineering/env-secrets-manager`, `engineering/secrets-vault-manager` | Use team skills for security analysis and response; use advanced skills for repeatable audits, dependency scans, and secrets workflows. |
| Data and ML | `engineering-team/senior-data-engineer`, `engineering-team/senior-data-scientist`, `engineering-team/senior-ml-engineer`, `engineering-team/senior-prompt-engineer` | `engineering/rag-architect`, `engineering/llm-cost-optimizer`, `engineering/statistical-analyst` | Use team skills for practitioner tasks; use advanced skills for RAG, LLM economics, and reusable analysis workflows. |
| Agent systems | `engineering-team/senior-prompt-engineer` | `engineering/agent-designer`, `engineering/agent-workflow-designer`, `engineering/agenthub`, `engineering/autoresearch-agent`, `engineering/llm-wiki` | Use senior-prompt-engineer for prompt/RAG support; use advanced skills for multi-agent systems and agent tooling. |
| Repository operations | `engineering-team/code-reviewer`, `engineering-team/senior-fullstack` | `engineering/git-worktree-manager`, `engineering/changelog-generator`, `engineering/release-manager`, `engineering/monorepo-navigator` | Use team skills for code changes; use advanced skills for repo-scale automation and release mechanics. |
| Documentation and runbooks | `engineering-team/senior-devops`, `engineering-team/incident-commander` | `engineering/runbook-generator`, `engineering/codebase-onboarding`, `engineering/demo-video` | Use team skills for operational judgment; use advanced skills to generate durable docs and onboarding artifacts. |

## Selection Rules

1. If the user asks for a role, start in `engineering-team/`.
2. If the user asks for a reusable workflow, platform pattern, agent, MCP, RAG,
   or audit tool, start in `engineering/`.
3. If both apply, load the role skill first, then add one advanced skill for the
   narrow workflow. Do not bulk-load both folders.
4. Keep folder names stable. Add cross-links or routing guidance instead of
   moving skills between folders.

## Maintenance Checklist

- New role/persona skill: place under `engineering-team/` unless it primarily
  builds reusable platform automation.
- New workflow/tooling skill: place under `engineering/` unless it is clearly a
  practitioner role.
- When adding a skill whose topic overlaps an existing one, update this matrix
  with the boundary and related skill link.
- Run `python scripts/validate-skill-frontmatter.py` after changing any
  `SKILL.md` or Gemini mirror output.
