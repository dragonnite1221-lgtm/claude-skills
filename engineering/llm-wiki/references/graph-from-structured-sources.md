# Building a Knowledge Graph from Structured Sources

Patterns validated in a production deployment that grew a real-entity knowledge
graph to ~110k entities / ~190k relations from official data APIs (corporate
registries, exchanges, patents, securities filings). They generalize the LLM
Wiki from *human-curated prose* to *machine-grown structured knowledge* without
losing the signal-over-noise discipline that makes the wiki worth reading.

The throughline: **the graph is built from real data, deterministically, and
its growth is measured.** Nothing enters by guesswork, and nothing operational
is allowed to dilute it.

## (a) Connector metadata → declarative entity extraction

When you ingest from a structured source (an API, a CSV, a registry dump), do
not let a model freely invent entities from the text. Instead, declare a small
mapping from *known fields* to *typed entities*:

- A field like `corp_code` / `cik` / `ticker` becomes a stable entity URI
  (`urn:entity:company:<authority>:<id>`), and the display name becomes its
  label.
- The mapping is data, not prose: a table of `(source field → entity type →
  URI template)`. New sources are onboarded by adding rows, not code.

The payoff is **stable identity**. Re-ingesting the same company tomorrow
resolves to the same URI, so the graph converges instead of sprouting
near-duplicates. The model is used for *labels and summaries*, never for
*identity*.

## (b) Typed, deterministic relations only

Every edge has a named predicate (`belongs_to_industry`, `listed_on_market`,
`same_as`, `covered_by_broker`) and is derived from an explicit field in the
source, with a pointer back to the evidence that produced it. Three rules keep
the edge set trustworthy:

- **No co-occurrence edges.** "Mentioned in the same document" is not a
  relationship. It is the single largest source of graph noise.
- **No LLM-guessed edges.** If a model has to *infer* that two entities are
  related, the edge does not belong in the deterministic layer.
- **Type the predicate.** An untyped "related-to" link carries no meaning and
  cannot be queried or trusted.

A smaller graph of typed, evidence-backed edges is worth more than a dense graph
of plausible-but-unverifiable ones. Identity links (`same_as`) across sources
are how you fuse a company's registry record, its ticker, and its securities
into one navigable hub.

## (c) Measure self-growth: health, lint, digest

A self-maintaining graph needs instruments, or you cannot tell growth from rot:

- **Health** — a periodic snapshot of entity count, relation count, orphan rate
  (entities with no edges), and average relations per entity. Append each
  snapshot to a history log and **flag regressions** (counts dropping, orphan
  rate climbing) the same way a test suite flags failures.
- **Lint** — structural checks: dangling URIs, untyped predicates, entities with
  a type but no identifying field, broken `same_as` chains.
- **Digest** — a periodic human-readable delta ("this week: +N entities, +M
  relations, orphan rate −X"), so a person can sanity-check direction without
  reading the graph.

Measure health on the **knowledge layer only**. Total edge count is a vanity
metric — it is trivially inflated by the noise patterns above.

## (d) Isolate telemetry from the knowledge graph

A live system generates operational state: run histories, queue depths, audit
ledgers, dashboards. This telemetry is regenerated every tick and is *not
knowledge*. If it lands in the same store as the knowledge graph it will:

- inflate link counts and orphan metrics with ephemeral pages,
- get pushed into your synced/version-controlled knowledge by accident,
- tempt readers to treat an audit console as a knowledge hub.

Keep them physically separate. Telemetry belongs on a **runtime surface** (a
live dashboard read straight from its real sources — the database, the process
journal, the event log), never in the graph. Knowledge hubs must be *real
entities* (companies, people, laws, sources), not status pages. A simple test:
if it is true only "as of this tick", it is telemetry, not knowledge.

## (e) Bulk-ingest a notes directory

To seed or backfill at scale, ingest an entire directory of notes/records in one
pass rather than one-by-one:

- Walk the tree, parse each record through the *same* declarative mapping (a),
  derive the *same* typed edges (b) — idempotently, so re-runs converge.
- Use short, lock-resilient transactions per record so a long backfill coexists
  with live writers instead of holding one giant lock.
- Skip already-present entities by default; offer an explicit "re-derive"
  switch for refreshing edges on entities that already exist.

Idempotency is the whole game: a backfill you can re-run safely is a backfill you
can trust, schedule, and resume after a failure.

## Why this stays an LLM Wiki

These patterns do not replace human curation — they extend it to a layer humans
could never maintain by hand. The model still does labels, summaries, and
crystallized answers; the *structure* is deterministic and measured. The human
still provides direction and judgment. The graph is just the bookkeeping made
free, exactly as in [memex-principles.md](memex-principles.md) — applied to
structured data instead of prose.
