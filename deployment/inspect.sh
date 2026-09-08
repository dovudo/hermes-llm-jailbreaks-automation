#!/usr/bin/env bash
# Inspect the machine + this package. Read-only. No installs, no attacks.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
echo "== lab root =="
echo "$ROOT"
echo "== python / docker / hermes =="
command -v python3 && python3 --version || echo "python3 MISSING"
python3 -c "import yaml; print('pyyaml', yaml.__version__)" 2>/dev/null || echo "pyyaml MISSING"
command -v docker && docker --version || echo "docker MISSING (needed only for agency canary)"
command -v hermes && hermes --version 2>/dev/null || echo "hermes not on PATH (expected on a fresh box until setup)"
echo "== package tree (top) =="
find "$ROOT" -maxdepth 2 -type d | sort
echo "== scope default =="
python3 "$ROOT/lib/scope_check.py" --config "$ROOT/configs/scope.example.yaml" --dump
echo "== deny test (must DENY) =="
python3 "$ROOT/lib/scope_check.py" --config "$ROOT/configs/scope.example.yaml" --target example.com || true
echo "== py_compile redteam =="
python3 -m py_compile \
  "$ROOT/projects/redteam/rt.py" \
  "$ROOT/projects/redteam/redteam/security.py" \
  "$ROOT/projects/redteam/redteam/report.py" \
  "$ROOT/lib/scope_check.py"
echo "inspect OK"
