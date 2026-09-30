#!/usr/bin/env bash
# review-new-skills.sh — Run Tessl + internal auditors on new/changed skills
#
# Usage:
#   ./scripts/review-new-skills.sh                    # Review all changed skills (vs dev)
#   ./scripts/review-new-skills.sh engineering/behuman # Review specific skill
#   ./scripts/review-new-skills.sh --all              # Review ALL skills (slow)
#   ./scripts/review-new-skills.sh --threshold 80     # Set minimum score (default: 70)

set -euo pipefail

THRESHOLD="${THRESHOLD:-70}"
SKILL_DIRS=()
MODE="changed"

# Parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
    --all)
      MODE="all"
      shift
      ;;
    --threshold)
      THRESHOLD="$2"
      shift 2
      ;;
    --help|-h)
      echo "Usage: $0 [--all] [--threshold N] [skill-dir ...]"
      echo ""
      echo "Options:"
      echo "  --all          Review all skills (not just changed ones)"
      echo "  --threshold N  Minimum Tessl score to pass (default: 70)"
      echo "  skill-dir      Specific skill directory to review"
      exit 0
      ;;
    *)
      SKILL_DIRS+=("$1")
      MODE="specific"
      shift
      ;;
  esac
done

# Determine which skills to review
if [ "$MODE" = "all" ]; then
  while IFS= read -r f; do
    dir=$(dirname "$f")
    SKILL_DIRS+=("$dir")
  done < <(find . -name SKILL.md -not -path './.codex/*' -not -path './.gemini/*' -not -path './docs/*' -not -path './eval-workspace/*' -not -path './medium/*' -not -path '*/assets/*' -maxdepth 3 | sed 's|^\./||' | sort)
elif [ "$MODE" = "changed" ] && [ ${#SKILL_DIRS[@]} -eq 0 ]; then
  echo "Detecting changed skills vs origin/dev..."
  CHANGED=$(git diff --name-only origin/dev...HEAD 2>/dev/null || git diff --name-only HEAD~1 2>/dev/null || echo "")
  if [ -z "$CHANGED" ]; then
    echo "No changes detected. Use --all or specify a skill directory."
    exit 0
  fi
  SEEN=()
  while IFS= read -r file; do
    dir=$(echo "$file" | cut -d'/' -f1-2)
    case "$dir" in
      .github/*|.claude/*|.codex/*|.gemini/*|docs/*|scripts/*|commands/*|standards/*|eval-workspace/*|medium/*) continue ;;
    esac
    if [ -f "$dir/SKILL.md" ] && [[ ! " ${SEEN[*]:-} " =~ " $dir " ]]; then
      SKILL_DIRS+=("$dir")
      SEEN+=("$dir")
    fi
  done <<< "$CHANGED"
fi

if [ ${#SKILL_DIRS[@]} -eq 0 ]; then
  echo "No skills to review."
  exit 0
fi

echo "================================================================"
echo "  SKILL QUALITY REVIEW"
echo "  Threshold: ${THRESHOLD}/100"
echo "  Skills: ${#SKILL_DIRS[@]}"
echo "================================================================"
echo ""

PASS_COUNT=0
FAIL_COUNT=0
RESULTS=()

for skill_dir in "${SKILL_DIRS[@]}"; do
  if [ ! -f "$skill_dir/SKILL.md" ]; then
    echo "⏭  $skill_dir — no SKILL.md, skipping"
    continue
  fi

  echo "━━━ $skill_dir ━━━"

  # 1. Tessl review
  TESSL_SCORE=0
  TESSL_EXIT=1
  TESSL_VALIDATION=FAIL
  if command -v tessl &>/dev/null; then
    TESSL_EXIT=0
    TESSL_JSON=$(tessl skill review "$skill_dir" --json 2>/dev/null) || TESSL_EXIT=$?
    TESSL_VALIDATION=$(printf '%s' "$TESSL_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print('PASS' if d.get('validation', {}).get('overallPassed') is True else 'FAIL')
except (ValueError, AttributeError):
    print('FAIL')
" 2>/dev/null) || TESSL_VALIDATION=FAIL
    TESSL_SCORE=$(echo "$TESSL_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(d.get('review', {}).get('reviewScore', 0))
except:
    print(0)
" 2>/dev/null || echo "0")
    TESSL_DESC=$(echo "$TESSL_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(round(d.get('descriptionJudge', {}).get('normalizedScore', 0) * 100))
except:
    print(0)
" 2>/dev/null || echo "0")
    TESSL_CONTENT=$(echo "$TESSL_JSON" | python3 -c "
import sys, json
try:
    d = json.load(sys.stdin)
    print(round(d.get('contentJudge', {}).get('normalizedScore', 0) * 100))
except:
    print(0)
" 2>/dev/null || echo "0")

    if [ "$TESSL_EXIT" -eq 0 ] && [ "$TESSL_VALIDATION" = "PASS" ] && [ "$TESSL_SCORE" -ge "$THRESHOLD" ]; then
      echo "  ✅ Tessl:    ${TESSL_SCORE}/100 (desc: ${TESSL_DESC}%, content: ${TESSL_CONTENT}%)"
    else
      echo "  ⚠️  Tessl:    ${TESSL_SCORE}/100 (desc: ${TESSL_DESC}%, content: ${TESSL_CONTENT}%) — review failed or below threshold"
    fi
  else
    echo "  ⏭  Tessl:    not installed (npm install -g tessl)"
  fi

  CHECKS=$(python3 scripts/required-skill-checks.py "$skill_dir" 2>/dev/null) || CHECKS="ERROR|ERROR|ERROR|FAIL"
  IFS='|' read -r STRUCT_SCORE SCRIPT_RESULT SEC_RESULT CHECK_RESULT <<< "$CHECKS"
  echo "  📐 Structure: $STRUCT_SCORE"
  echo "  🧪 Scripts:  $SCRIPT_RESULT"
  echo "  🔒 Security: $SEC_RESULT"

  # Verdict
  if [ "$TESSL_EXIT" -eq 0 ] && [ "$TESSL_VALIDATION" = "PASS" ] && [ "$TESSL_SCORE" -ge "$THRESHOLD" ] && [ "$CHECK_RESULT" = "PASS" ]; then
    PASS_COUNT=$((PASS_COUNT + 1))
    RESULTS+=("✅ $skill_dir: ${TESSL_SCORE}/100")
  else
    FAIL_COUNT=$((FAIL_COUNT + 1))
    RESULTS+=("⚠️  $skill_dir: ${TESSL_SCORE}/100 — review failed, score below ${THRESHOLD}, or required check failed")
  fi

  echo ""
done

echo "================================================================"
echo "  SUMMARY"
echo "================================================================"
for r in "${RESULTS[@]}"; do
  echo "  $r"
done
echo ""
echo "  Pass: $PASS_COUNT | Below threshold: $FAIL_COUNT"
echo "================================================================"

if [ "$FAIL_COUNT" -gt 0 ]; then
  exit 1
fi
