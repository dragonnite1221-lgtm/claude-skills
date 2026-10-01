#!/usr/bin/env bash
set -euo pipefail

script="$(cd "$(dirname "$0")/.." && pwd)/scripts/codex-install.sh"
root="$(mktemp -d)"
trap 'rm -rf -- "$root"' EXIT
mkdir -p "$root/skills"
printf 'keep\n' > "$root/sentinel"

if CODEX_SKILLS_DIR="$root/skills" bash "$script" --skill ../../sentinel >/dev/null 2>&1; then
    echo "traversal name was accepted" >&2
    exit 1
fi
[[ "$(cat "$root/sentinel")" == keep ]]

CODEX_SKILLS_DIR="$root/skills" bash "$script" --all --dry-run > "$root/output"
grep -q 'Installation complete:' "$root/output"
