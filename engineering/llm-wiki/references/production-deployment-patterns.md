# Production deployment patterns — scaling the wiki into a maintained graph

Lessons from running this pattern at scale (thousands of pages, automated daily
ingestion). These generalize the three core operations (ingest / query / lint)
into a self-maintaining **knowledge graph** layer. Tool-agnostic; adapt the
mechanics to your stack.

## 1. From wikilinked pages to a typed entity graph

Wikilinks alone give navigation but not structure. At scale, promote two things
to first-class, queryable records alongside the markdown pages:

- **Entities** — the real things pages are about (people, orgs, places,
  companies, laws, papers). Each has a stable URI, a human label, and a type.
- **Typed relations** — `(subject, predicate, object)` triples between entities
  (e.g. `belongs_to`, `same_as`, `filed_by`, `subject_to`). These are what make
  the graph *organic* rather than a flat page list.

Render each entity as its own page (provenance + inbound/outbound links) so the
graph hubs are **real entities**, not process artifacts.

## 2. Declarative extraction (one rule table, not N edits)

When sources arrive with structured identifiers in their metadata
(`corp_code`, `cik`, `doi`, `law_id`, a ticker…), derive entities/relations from
a single **source → rule** map applied at the ingestion boundary — instead of
hand-editing every connector/importer. Adding a new source becomes one rule
entry. Explicit, source-provided graph refs always win over derived ones.

## 3. Anti-noise rule: typed + deterministic only

The fastest way to ruin a knowledge graph is to auto-create edges from
**co-occurrence** or **LLM guesses**. The graph fills with plausible-looking but
meaningless links — "knowledge theater." Enforce:

- Relations come only from **structured fields or verified sources**, are
  **typed** (a small controlled predicate vocabulary), and have both endpoints
  as real entities.
- Skip a relation when its required field is missing. No edge is better than a
  noisy edge.

## 4. Quarantine telemetry from the knowledge graph

Automation tends to emit operational notes (run logs, audit/status dashboards,
queues). These are **not knowledge** and must never become graph hubs — left
unchecked they dominate the link graph and drown real content. Keep them in a
separate area, exclude them from the graph view, and **measure graph health on
the knowledge layer only** (never on total link/node count, which telemetry
inflates).

## 5. Measure compounding (so "it improves over time" is provable)

Add three automated health surfaces over the entity graph:

- **Health metrics** — entity count, relation count, orphan rate, average
  relations per entity, top hubs. A healthy second brain shows **density rising
  and orphan rate falling** over time.
- **Lint** — broken relation endpoints, orphan entities (no relations), entities
  with no supporting evidence, duplicate labels.
- **Digest** — periodic summary of new entities/relations, new hubs, and
  unresolved contradictions.

Snapshot the metrics to an append-only history and alert on regression.

## 6. Human-readable hubs

Category/grouping hub nodes (industries, topics, jurisdictions) should carry a
**human name**, not a raw code. A code-labeled hub is unreadable; a named hub is
a navigable cluster. Keep the code→name map small and in a low-level module.

## 7. Cross-source identity (`same_as`)

The same real entity arrives from multiple sources under different ids. Link
them with a `same_as` relation (deterministically — e.g. via a shared listing
code), so one company/person/work is one node, not many fragments.

## 8. Validity windows for changing facts

When a relation has an effective date in the source (a filing date, an
enactment date), record `effective_from`/`effective_to` on the relation. A
query can then ask "what was true as of <date>" rather than only "now."

## 9. Absorb existing silos as personal notes

Scattered notes (chat logs, meeting notes, other apps' exports) become
first-class graph nodes by batch-ingesting a directory as personal-class
entities — unifying knowledge that was previously stranded. Skip files that may
carry secrets.

## 10. Contradictions are a review queue, not a deletion

When two sources conflict, surface the pair in a contradiction review queue
(grouped by topic) instead of silently picking one. The human resolves; the
graph never loses the disagreement.

---

These extend, not replace, `ingest-workflow.md` / `query-workflow.md` /
`lint-workflow.md`. Start with the three core operations; add the graph layer
once you have enough pages that flat navigation stops scaling.
