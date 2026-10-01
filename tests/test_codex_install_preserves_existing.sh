#!/usr/bin/env bash
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tmp=$(mktemp -d /tmp/codex-install-preserve.XXXXXX)
trap 'case "$tmp" in /tmp/codex-install-preserve.*) rm -rf -- "$tmp";; esac' EXIT

mkdir -p "$tmp/repo/scripts" "$tmp/repo/.codex/skills/demo" "$tmp/dest/demo"
cp "$repo_root/scripts/codex-install.sh" "$tmp/repo/scripts/codex-install.sh"
printf 'old\n' > "$tmp/dest/demo/sentinel"
printf 'new\n' > "$tmp/repo/.codex/skills/demo/SKILL.md"
ln -s missing "$tmp/repo/.codex/skills/demo/broken"

if CODEX_SKILLS_DIR="$tmp/dest" bash "$tmp/repo/scripts/codex-install.sh" --skill demo >/dev/null 2>&1; then
    echo 'Expected staged copy to fail' >&2
    exit 1
fi
[[ $(cat "$tmp/dest/demo/sentinel") == old ]]

rm "$tmp/repo/.codex/skills/demo/broken"
CODEX_SKILLS_DIR="$tmp/dest" bash "$tmp/repo/scripts/codex-install.sh" --skill demo >/dev/null
[[ $(cat "$tmp/dest/demo/SKILL.md") == new ]]
[[ ! -e "$tmp/dest/demo/sentinel" ]]
