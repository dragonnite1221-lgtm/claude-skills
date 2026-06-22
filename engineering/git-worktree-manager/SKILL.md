---
name: "git-worktree-manager"
description: "Create and tear down isolated git worktrees for parallel branch work — auto-allocates non-conflicting ports (app/DB/Redis) per worktree, persists them to .worktree-ports.json, copies .env* files from the main repo, optionally installs deps, and safely removes stale/merged/clean worktrees. Use when running 2+ branches locally at once, giving each agent or terminal its own isolated dev server, shipping a hotfix while a feature branch is dirty, or replacing ad-hoc `rm -rf` worktree cleanup — e.g. 'set up a worktree for this feature', 'run two branches in parallel', or 'clean up old worktrees'."
---

# Git Worktree Manager

Runs parallel feature work safely with Git worktrees: deterministic branch
isolation, per-worktree port allocation, `.env` sync, and guarded cleanup so each
worktree behaves like an independent local app. Optimized for multi-agent workflows
where each agent or terminal session owns one worktree.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/worktree_manager.py` | Create a worktree, allocate + persist ports, copy `.env*`, optionally install deps |
| `scripts/worktree_cleanup.py` | Detect stale/dirty/merged worktrees and safely remove them |

Both accept flags, a `--input file.json`, or piped stdin JSON, and emit
`--format text` (human) or `--format json` (automation).

## Create a worktree

```bash
python scripts/worktree_manager.py \
  --repo . \
  --branch feature/new-auth \
  --name wt-auth \
  --base-branch main \
  --install-deps \
  --format text

# automation: feed config via file or stdin
python scripts/worktree_manager.py --input config.json --format json
cat config.json | python scripts/worktree_manager.py --format json
```

The script creates the branch if missing, writes `.worktree-ports.json` into the
worktree with unique app/DB/Redis ports, and copies any `.env*` files from the main
repo. Tune ports with `--app-base` (3000), `--db-base` (5432), `--redis-base`
(6379), and `--stride` (10).

**Verify setup:** `git worktree list` shows the path + branch, `.worktree-ports.json`
holds unique ports, and the app boots on the allocated app port. If env copy or dep
install fails, the worktree is still created — recover those steps manually.

## Cleanup with safety checks

```bash
python scripts/worktree_cleanup.py --repo . --stale-days 14 --format text   # scan only
python scripts/worktree_cleanup.py --repo . --remove-merged --base-branch main --format text
```

`--remove-merged` removes only worktrees that are stale, clean, *and* merged into
`--base-branch`. `--force` allows removal of dirty trees — use only when discarding
changes is intentional. Run a scan weekly in active repos.

## Conventions

- One branch per worktree, one agent per worktree; keep them short-lived.
- Deterministic names mapping to a task (`wt-1234-auth`); never reuse port 3000
  across branches or share one DB URL between isolated feature branches.
- Persist port mappings in `.worktree-ports.json`, not terminal notes.
- Never create a worktree inside the main repo directory.
- Choose a worktree only when you need isolated deps/ports (new feature, hotfix on a
  dirty branch, ephemeral bug repro); for a quick diff review, stay on the current tree.

## References

- [port-allocation-strategy.md](references/port-allocation-strategy.md) — `base + (index * stride)` allocation, collision handling, edge cases
- [docker-compose-patterns.md](references/docker-compose-patterns.md) — per-worktree compose overrides mapped from the allocated port map
- [README.md](README.md) — quick start and installation
