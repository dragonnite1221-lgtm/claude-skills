---
name: code-to-prd
description: |
  Reverse-engineer a frontend, backend, or fullstack codebase into a complete Product
  Requirements Document. Scans routes/pages, components, state, API calls, database models,
  enums, and mock-vs-real data with codebase_analyzer.py, then scaffolds a structured prd/
  directory (README, per-page docs, enum dictionary, API inventory) with prd_scaffolder.py —
  detailed enough for an engineer or AI agent to reconstruct every page and endpoint in
  business language. Use when the user says "generate a PRD from this code",
  "reverse-engineer requirements", "document this codebase / its pages / API endpoints",
  "extract product specs from code", or "create a functional inventory". Covers React, Vue,
  Angular, Svelte, Next.js, Nuxt, SvelteKit, Remix, Astro, NestJS, Express, Fastify,
  Django/DRF, FastAPI, and Flask.
license: MIT
metadata:
  updated: 2026-03-17
  author: Alireza Rezvani
  version: 2.1.2
  tier: STANDARD
  category: product
---

# Code → PRD: Reverse-Engineer Any Codebase into Product Requirements

Read a codebase, understand every page/endpoint's business purpose, and produce a PRD in
**product-manager-friendly language** — non-technical phrasing, zero business detail omitted.

**Dual audience:** PMs/stakeholders need to know *what* the system does; engineers/AI agents
need enough detail to **fully reconstruct** every page's fields, interactions, and relationships.

## Quick Start

Both scripts are **stdlib-only** (no pip install).

```bash
# 1. Scan the project → analysis JSON (frontend, backend, or fullstack)
python3 scripts/codebase_analyzer.py /path/to/project -o analysis.json

# 2. (optional) Eyeball a human-readable summary of what was detected
python3 scripts/codebase_analyzer.py /path/to/project -f markdown

# 3. Validate the analysis, then scaffold the prd/ directory
python3 scripts/prd_scaffolder.py analysis.json --validate-only
python3 scripts/prd_scaffolder.py analysis.json -o prd/ -n "My App"

# Or drive the whole thing through the slash command:
/code-to-prd /path/to/project
```

Use `--dry-run` on the scaffolder to preview file creation. If step 3 reports a validation
error, fix the analysis JSON (or re-run step 1) before scaffolding. Then fill in each stub
page-by-page using Phase 2 below.

For backend-only projects, "page" maps to **API resource groups** or **admin views** — routes
become endpoints, components become controllers/views, interactions become request/response flows.

---

## Workflow

### Phase 1 — Project Global Scan

Build global context before diving into pages. The analyzer detects most of this; verify and fill gaps.

1. **Identify the framework** from `package.json` (Node), `manage.py` (Django), or
   `requirements.txt`/`pyproject.toml` (Python). Routing/state/component patterns differ per
   framework — see [framework-patterns.md](references/framework-patterns.md) for the directory
   conventions, route extraction, and mock-detection signals per stack.
2. **Build a page (or endpoint) inventory** — route path, title, module/menu level, and source
   file per page. For file-system routing (Next.js, Nuxt), infer from directory structure. For
   backends, capture HTTP method, controller/view, owning module/app, and auth requirement
   (`@Controller`+`@Get/@Post`… for NestJS; `urlpatterns` + router registrations for Django).
3. **Map global context** — global state (user/permissions/feature flags), shared components
   (layout, nav, auth guards), enums & constants, API base config (base URL, interceptors,
   auth headers), DB models/entities, middleware, and DTOs/serializers.

### Phase 2 — Page-by-Page Deep Analysis

Analyze every page in the inventory. **Each page produces its own Markdown file.** For each, document:

- **A. Overview** — what the page does (one sentence), where it fits, what brings a user here.
- **B. Layout & regions** — search area, table, detail panel, action bar, tabs; spatial arrangement.
- **C. Field inventory (core — be exhaustive).** For forms, list every field as
  `Field | Type | Required | Default | Validation | Business description`. For tables/lists,
  list filter fields, columns (format/sortable/filterable), and row actions. Resolve field
  display names in priority order: hardcoded text → i18n values → `placeholder`/`label`/`title`
  props → variable names (last resort).
- **D. Interaction logic** — describe as **action → response**, e.g.:
  `[Action] click "Create" → [Response] modal with fields … → [Validation] name required →
  [API] POST /api/user/create → [Success] toast + refresh list → [Failure] show API error`.
  Cover load/init, search/filter/reset, CRUD, pagination/sorting/bulk actions, validation,
  status transitions, import/export, field interdependencies, permission-gated controls, polling.
- **E. API dependencies.** If real HTTP calls exist, tabulate `API | Method | Path | Trigger |
  Params | Notes`. If the page uses mock data (`setTimeout`/`Promise.resolve()` returning data,
  `*.mock.*` files, `__mocks__/`, hardcoded fixtures), **reverse-engineer the required API spec**
  (method, suggested path, inputs, outputs, business logic) and mark it as not-yet-integrated.
- **F. Page relationships** — inbound links (+params), outbound navigation (+params), data coupling.

### Phase 3 — Generate Documentation

Run `prd_scaffolder.py` (Quick Start step 3), then fill the stubs. The scaffolder writes:

```
prd/
├── README.md                  # System overview, module table, page inventory, global notes
├── pages/01-*.md, 02-*.md …   # One stub per page/endpoint (overview, layout, fields,
│                              #   interactions, API deps, relationships, business rules)
└── appendix/
    ├── enum-dictionary.md      # Every enum/status code/type mapping (value + meaning)
    ├── page-relationships.md   # Navigation map between pages
    └── api-inventory.md        # Complete API reference
```

Each stub ships with section headers and empty tables. Keep each page file **self-contained**
(reading it alone gives full understanding) and cross-reference others with relative links.
Validate the result against [prd-quality-checklist.md](references/prd-quality-checklist.md).

---

## Key Principles

1. **Business language first.** Write "search button shows a spinner to prevent duplicate
   submissions," not "calls `useState` to manage loading." Include technical detail only when it
   affects product behavior (API paths, validation rules, permission conditions).
2. **Don't miss hidden logic** — field interdependencies, conditional button visibility, data
   formatting (currency/date/status-label maps), default sort order and page size, debounce,
   polling intervals.
3. **Exhaustively list enums.** Every status code, type code, and role — value + meaning. They're
   scattered across constants files, `valueEnum` configs, and response mappers.
4. **Mark uncertainty — don't guess.** If business meaning can't be determined from code, mark it
   `[TBC]`, state what you observed, and explain the uncertainty. Never fabricate meaning.

## Execution Pacing

- **Large projects (>15 pages):** complete system overview + page inventory first, then work in
  batches of 3–5 pages per module; output each batch for review before proceeding.
- **Small projects (≤15 pages):** complete all analysis in one pass.

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Component names as page names | `UserManagementTable` → "User Management List" |
| Skipping modals/drawers | They hold critical business logic — document fully (as part of the triggering page) |
| Missing i18n field names | Check translation files, not just JSX |
| Ignoring dynamic route params | `/order/:id` means the page requires an order ID to load |
| Forgetting permission controls | Document which roles see which buttons/pages |
| Assuming all APIs are real | Check for mock patterns before documenting endpoints |
| Skipping Django `admin.py` | Holds list filters, custom actions, inlines — often critical rules |
| Missing NestJS guards/pipes | `@UseGuards`/`@UsePipes` carry auth and validation logic |
| Ignoring DB constraints | `unique`, `max_length`, `choices` are validation rules for the PRD |

---

## References

| File | Contents |
|------|----------|
| [framework-patterns.md](references/framework-patterns.md) | Per-framework routes, state, APIs, forms, permissions, mock-detection signals |
| [prd-quality-checklist.md](references/prd-quality-checklist.md) | Validation checklist for completeness, accuracy, readability |

`assets/sample-analysis.json` is a reference analysis JSON for testing the scaffolder.

## Attribution

Inspired by [code-to-prd](https://github.com/lihanglogan/code-to-prd) by
[@lihanglogan](https://github.com/lihanglogan) ([PR #368](https://github.com/alirezarezvani/claude-skills/pull/368)).
The three-phase workflow (global scan → page-by-page analysis → structured generation) originated
there; this version was rebuilt in English with added tooling and references.
