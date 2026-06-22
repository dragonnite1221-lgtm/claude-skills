---
title: "Changelog Generator — Agent Skill for Codex & OpenClaw"
description: "Generate Keep-a-Changelog release notes from Conventional Commits and infer the SemVer bump (major/minor/patch) with generate_changelog.py — reads. Agent skill for Claude Code, Codex CLI, Gemini CLI, OpenClaw."
---

# Changelog Generator

<div class="page-meta" markdown>
<span class="meta-badge">:material-rocket-launch: Engineering - POWERFUL</span>
<span class="meta-badge">:material-identifier: `changelog-generator`</span>
<span class="meta-badge">:material-github: <a href="https://github.com/alirezarezvani/claude-skills/tree/main/engineering/changelog-generator/SKILL.md">Source</a></span>
</div>

<div class="install-banner" markdown>
<span class="install-label">Install:</span> <code>claude /plugin install engineering-advanced-skills</code>
</div>


Produce consistent, auditable release notes from Conventional Commits. Commit
parsing, semver bump logic, and changelog rendering are separated so teams can
automate releases while keeping editorial control. Two stdlib-only tools.

## Tools

| Tool | Purpose |
|------|---------|
| `scripts/generate_changelog.py` | Conventional commits → Keep-a-Changelog entry + semver bump |
| `scripts/commit_linter.py` | Validate commit subject format (PR gate with `--strict`) |

## Workflow

Lint first to gate the range, then generate. If the linter reports violations,
fix the commits and re-run; if generation finds no valid commits, it fails early
rather than emitting empty notes.

```bash
# 1. Lint commits for the release range (CI gate; --strict exits non-zero on violations).
python3 scripts/commit_linter.py --from-ref origin/main --to-ref HEAD --strict --format text
python3 scripts/commit_linter.py --input commits.txt --strict
cat commits.txt | python3 scripts/commit_linter.py --format json

# 2. Generate an entry from a git tag range.
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag v1.4.0 --next-version v1.4.0 --format markdown

# 3. Or from stdin / a file.
git log v1.3.0..v1.4.0 --pretty=format:'%s' | \
  python3 scripts/generate_changelog.py --next-version v1.4.0 --format markdown
python3 scripts/generate_changelog.py --input commits.txt --next-version v1.4.0 --format json

# 4. Prepend the entry into CHANGELOG.md (keeps prior sections).
python3 scripts/generate_changelog.py \
  --from-tag v1.3.0 --to-tag HEAD --next-version v1.4.0 --write CHANGELOG.md
```

`generate_changelog.py` also takes `--from-ref/--to-ref` and `--date YYYY-MM-DD`.
Tag the release only after the changelog is generated and approved.

## Conventional Commit rules

Types: `feat`, `fix`, `perf`, `refactor`, `docs`, `test`, `build`, `ci`,
`chore`, `security`, `deprecated`, `remove`. Breaking change via `type(scope)!:`
or a `BREAKING CHANGE:` footer/body. SemVer mapping: breaking → `major`,
non-breaking `feat` → `minor`, all others → `patch`.

## Output quality checks

- Each bullet is user-meaningful, not implementation noise.
- Breaking changes include a migration action.
- Security fixes isolated in a `Security` section; empty sections omitted; duplicates removed.

## Common pitfalls

1. Mixing merge-commit messages into release parsing.
2. Vague summaries that can't become release notes.
3. No migration guidance for breaking changes.
4. Treating docs/chore changes as user-facing features.
5. Overwriting historical sections instead of prepending.

In monorepos, scope commits to package names (`feat(api): ...`) and filter the
stream by scope for package-specific releases; keep infra-wide changes in the
root changelog.

## References

- [references/ci-integration.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/changelog-generator/references/ci-integration.md) — PR linting + tag-push release automation
- [references/changelog-formatting-guide.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/changelog-generator/references/changelog-formatting-guide.md) — Keep a Changelog sections and wording
- [references/monorepo-strategy.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/changelog-generator/references/monorepo-strategy.md) — scoped/per-package changelog strategy
- [README.md](https://github.com/alirezarezvani/claude-skills/tree/main/engineering/changelog-generator/README.md)
