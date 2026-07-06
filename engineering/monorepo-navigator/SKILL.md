---
name: "monorepo-navigator"
description: "Detect a monorepo's tool (Turborepo, Nx, pnpm/yarn workspaces, Lerna), enumerate its workspaces, and build the internal package dependency graph from a repo path using monorepo_analyzer.py (text or --json). Guides cross-package impact analysis, selective/affected-only builds and tests, remote caching, multi-repo→monorepo migration with git history preserved, Changesets publishing, and workspace-aware CLAUDE.md setup. Use when shared packages make builds slow, when you need to know which apps break if a shared package changes, when migrating polyrepo→monorepo, or when setting up coordinated npm publishing — e.g. 'analyze my monorepo structure', 'which packages are affected by this change', 'set up Turborepo caching'."
---

# Monorepo Navigator

Navigate, analyze, and optimize JS/TS monorepos. The analyzer detects the
toolchain and maps internal package dependencies; the references cover build
optimization, migration, and publishing patterns.

## Workspace analyzer

`scripts/monorepo_analyzer.py PATH` detects the monorepo type, workspace
patterns, and the internal dependency graph between packages.

```bash
python3 scripts/monorepo_analyzer.py /path/to/monorepo          # human-readable
python3 scripts/monorepo_analyzer.py /path/to/monorepo --json   # machine-readable
```

If it reports `Detected: none`, the path isn't a recognized monorepo root —
point it at the directory containing the root `package.json` /
`pnpm-workspace.yaml` / `nx.json` and re-run. Use `--json` to feed impact
analysis into CI affected-package selection.

## Tool selection

| Tool | Best for | Key feature |
|------|----------|-------------|
| Turborepo | JS/TS monorepos, simple pipelines | Best-in-class remote caching, minimal config |
| Nx | Large enterprises, plugin ecosystem | Project graph, code generation, affected commands |
| pnpm workspaces | Workspace protocol, disk efficiency | `workspace:*` local package refs |
| Lerna | npm publishing, versioning | Batch publishing |
| Changesets | Modern versioning (preferred over Lerna) | Changelog generation, pre-release channels |

Most modern setups: **pnpm workspaces + Turborepo + Changesets**.

## When to use

Use when multiple packages share code, builds rebuild everything on any change,
you're migrating polyrepo→monorepo, or you need coordinated npm publishing.
Skip for single-app projects, fully isolated team boundaries, or when shared
code is minimal enough that copy-paste is acceptable.

## Common pitfalls

| Pitfall | Fix |
|---------|-----|
| `turbo run build` without `--filter` on every PR | Use `--filter=...[origin/main]` in CI |
| `workspace:*` refs cause publish failures | `pnpm changeset publish` replaces them with real versions |
| All packages rebuild on an unrelated change | Tune `inputs` in turbo.json to exclude docs/config from cache keys |
| Shared tsconfig breaks one package's type-check | Use `extends`; each package overrides `rootDir`/`outDir` |
| git history lost during migration | `git filter-repo --to-subdirectory-filter` before merging — never move files manually |
| Remote cache not working in CI | Check `TURBO_TOKEN`/`TURBO_TEAM`; verify with `turbo run build --summarize` |
| Generic CLAUDE.md — Claude edits the wrong package | Add per-package "only touch files in apps/X" rules |

## Best practices

1. Root CLAUDE.md is the map (every package, purpose, dependency rules);
   per-package CLAUDE.md is the rules (allowed/forbidden, test commands).
2. Always scope commands with `--filter` — running everything defeats the purpose.
3. Remote caching is not optional; without it monorepo CI is slower than polyrepo.
4. Changesets over hand-edited `package.json` versions.
5. Shared configs in root (`tsconfig.base.json`, etc.), extended per package.
6. Run impact analysis before merging shared-package changes; communicate blast radius.
7. Keep `packages/types` as pure TypeScript — no runtime code, fast to build.

## References

- [references/monorepo-tooling-reference.md](references/monorepo-tooling-reference.md) — Turborepo/Nx/pnpm/Changesets details
- [references/monorepo-patterns.md](references/monorepo-patterns.md) — architecture and CI patterns
