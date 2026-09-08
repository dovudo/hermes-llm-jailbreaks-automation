#!/usr/bin/env bash
# Remove optional skill copies and stop local canary if we started it.
# Does NOT uninstall Hermes. Does NOT delete the package tree unless --purge-tree.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_HOME="${HERMES_HOME:-$HOME/.hermes}"
echo "Stopping agency canary if compose exists (lab copy only)..."
if [[ -f "$ROOT/projects/redteam/agency/docker-compose.yml" ]] && command -v docker >/dev/null; then
  (cd "$ROOT/projects/redteam/agency" && docker compose down) || true
fi
if [[ -d "$HERMES_HOME/skills/security-lab" ]]; then
  echo "Removing $HERMES_HOME/skills/security-lab"
  rm -rf "$HERMES_HOME/skills/security-lab"
fi
if [[ "${1:-}" == "--purge-tree" ]]; then
  echo "Refusing to rm package from inside script. Delete $ROOT yourself if intended."
fi
echo "uninstall done"
