#!/usr/bin/env bash
# Optional install onto THIS machine's Hermes skills dir.
# Does not start attacks. Does not write secrets.
# Read this script before running.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
SKILLS_DST="${HERMES_HOME}/skills/security-lab"
DRY="${1:-}"

echo "LAB_ROOT=$ROOT"
echo "SKILLS_DST=$SKILLS_DST"
echo "This copies bundled skills and creates engagement/ with empty scope."
echo "It will NOT run rt.py full, will NOT start hermes proxy, will NOT scan the internet."

if [[ "$DRY" != "--yes" ]]; then
  echo "Re-run with: $0 --yes"
  exit 0
fi

mkdir -p "$ROOT/engagement/evidence"
cp -n "$ROOT/configs/authorization.example.md" "$ROOT/engagement/authorization.md" 2>/dev/null || true
# hosts-only empty allowlist
: > "$ROOT/engagement/scope.txt"
echo "# empty default allowlist" >> "$ROOT/engagement/scope.txt"

mkdir -p "$SKILLS_DST"
# copy bundled skills if hermes home exists
if [[ -d "$HERMES_HOME/skills" ]]; then
  rsync -a "$ROOT/skills/bundled/" "$SKILLS_DST/"
  echo "copied skills -> $SKILLS_DST"
else
  echo "Hermes skills dir not found; skipped skill copy. Unpack is enough for the receiving agent."
fi

# canary data dir for nobody uid — only if docker will be used later
mkdir -p "$ROOT/projects/redteam/agency/data" "$ROOT/projects/redteam/out"
echo "install (non-attack) done"
