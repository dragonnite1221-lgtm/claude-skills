#!/usr/bin/env bash
set -euo pipefail

source_script="$(cd "$(dirname "$0")/.." && pwd)/scripts/convert.sh"
root="$(mktemp -d)"
trap 'rm -rf -- "$root"' EXIT
mkdir -p "$root/scripts" "$root/category/first" "$root/output/cursor"
sed 's/\r$//' "$source_script" > "$root/scripts/convert.sh"
printf 'keep\n' > "$root/output/cursor/sentinel"
cat > "$root/category/first/SKILL.md" <<'EOF'
---
name: ../../outside
description: test
---
body
EOF

if bash "$root/scripts/convert.sh" --tool cursor --out "$root/output" >/dev/null 2>&1; then
  echo "unsafe name accepted" >&2
  exit 1
fi
[[ "$(cat "$root/output/cursor/sentinel")" == keep ]]
[[ ! -e "$root/outside" ]]

sed -i 's@../../outside@shared@' "$root/category/first/SKILL.md"
mkdir -p "$root/category/second"
cp "$root/category/first/SKILL.md" "$root/category/second/SKILL.md"
if bash "$root/scripts/convert.sh" --tool cursor --out "$root/output" >/dev/null 2>&1; then
  echo "duplicate name accepted" >&2
  exit 1
fi
[[ "$(cat "$root/output/cursor/sentinel")" == keep ]]

rm "$root/category/second/SKILL.md"
bash "$root/scripts/convert.sh" --tool cursor --out "$root/output" >/dev/null
[[ -f "$root/output/cursor/rules/shared.mdc" ]]
