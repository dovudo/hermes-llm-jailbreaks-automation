#!/usr/bin/env bash
# Harmless smoke. No live LLM calls. No external targets.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail=0

python3 -m py_compile \
  "$ROOT/lib/scope_check.py" \
  "$ROOT/projects/redteam/rt.py" \
  "$ROOT/projects/redteam/redteam/security.py" \
  "$ROOT/projects/redteam/redteam/report.py" \
  "$ROOT/projects/redteam/static/harness.py" \
  "$ROOT/projects/redteam/adaptive/adaptive_attack.py" \
  "$ROOT/projects/redteam/agency/cascade.py" \
  "$ROOT/projects/redteam/agency/tool_server.py" || fail=1

python3 "$ROOT/lib/scope_check.py" --config "$ROOT/configs/scope.example.yaml" --target 8.8.8.8 >/tmp/scope-deny.txt || true
grep -q DENY /tmp/scope-deny.txt || { echo "scope_check should DENY 8.8.8.8"; fail=1; }

# empty allowlist must deny localhost too (default has no hosts)
python3 "$ROOT/lib/scope_check.py" --config "$ROOT/configs/scope.example.yaml" --target 127.0.0.1 >/tmp/scope-local.txt || true
grep -q DENY /tmp/scope-local.txt || { echo "default scope must DENY localhost until listed"; fail=1; }

# dry-pack does not call LLMs
if command -v python3 >/dev/null; then
  python3 -c "import yaml" 2>/dev/null || echo "WARN: pyyaml missing (rt.py needs it)"
fi

# secret scan (heuristic)
if grep -R -n -E 'sk-[A-Za-z0-9]{10,}|-----BEGIN [A-Z ]*PRIVATE KEY-----|ghp_[A-Za-z0-9]{20,}|xox[baprs]-' \
  --exclude-dir='.git' "$ROOT" | grep -v 'CREDENTIALS.md' | grep -v '<REDACTED>' ; then
  echo "SECRET SCAN HIT"
  fail=1
else
  echo "secret scan: no private-key/token patterns"
fi

echo "verify exit=$fail (0=ok). Live red-team NOT run."
exit "$fail"
