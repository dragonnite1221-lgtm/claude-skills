# Fleet Quality Invariants

> Reference implementation in this repository. Once proven here, this document
> and its CI plumbing are promoted to the control-plane repo
> (`openclaw-workspace`) as a shared standard + reusable GitHub Actions
> workflow that every repo adopts.

## Why these exist

Almost every defect found in the June 2026 fleet-wide refactor was the **same
bug wearing different clothes**: a *declared* state (a number in a doc, a
committed generated file, "it passes locally", a green-but-never-run CI badge,
a "we support 3.10" claim) silently diverged from the *actual* state, because
nothing continuously checked that the two matched.

These invariants close that gap. Each one asserts **declared == actual** and
fails the build the moment they diverge — at the point of introduction, not
weeks later in an analysis pass.

## The five invariants

### 1. Generated artifacts are gate-checked, never hand-maintained

Anything a script can produce (inventory counts, the `.gemini` mirror, codex
mirrors) is produced by that script and **regenerated in CI**; the build fails
if the committed copy drifts.

- Source: `scripts/count-repository-items.py --write` → `documentation/INVENTORY.md`
- Gate: `scripts/count-repository-items.py --check` (byte-equality)
- Prose must **point to** the generated file, never restate its numbers.

Reference: the Gemini mirror gate (`scripts/validate-skill-frontmatter.py`)
and the inventory gate above.

### 2. Local == CI

A developer's local check and CI run the **same script**, so a green local run
cannot be a false signal (the failure mode behind evidence-os's "346 files
locally vs 550 in CI" mypy miss).

- One entry point: `scripts/check.sh`. CI calls it; you call it before pushing.

### 3. Tests are hermetic

A test must pin its own environment and never read ambient host state. A test
whose result depends on the machine it runs on is not testing the code.

- Pin: git identity **and** `commit.gpgsign=false` in throwaway repos; `TERM`
  and locale when output glyphs depend on them; treat timeouts as **ordering**
  budgets, not latency assertions.
- Reference: codegraph `__tests__` (git-signing, `TERM`, CPU-starvation guards).

### 4. The declared support matrix is actually exercised

If a project declares `python >=3.10` or `node >=18`, CI runs the **floor** of
that range. (CLI-Anything declared `>=3.10` but only an untested f-string
broke on 3.10/3.11.)

### 5. A gate must go green once before it merges

A CI workflow added in a PR must have a **successful run on that PR** before
merge. A gate that has never passed is theatre (the Tessl gate sat red for
days because its token/parsing path was never validated end-to-end).

## Adoption checklist (per repo)

- [ ] Generated files have a `--write`/`--check` pair and a CI drift gate (Inv. 1)
- [ ] A single `check` entry point that CI and humans both run (Inv. 2)
- [ ] Test fixtures pin git/TERM/locale; timeouts assert order not latency (Inv. 3)
- [ ] CI matrix includes the declared minimum runtime version (Inv. 4)
- [ ] Every new gate has one green run on its introducing PR (Inv. 5)
