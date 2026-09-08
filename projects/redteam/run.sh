#!/usr/bin/env bash
# Unified red-team suite control.
#   ./run.sh up|smoke
#   ./run.sh static|adaptive|agency [--target MODEL] [--allow-fire]
#   ./run.sh full [--target MODEL] [--allow-fire]
#   ./run.sh prompt --text '...' [--target MODEL] [--layers all|static|adaptive|agency] [--dry-pack]
#   ./run.sh report [--out-md PATH]
set -euo pipefail
cd "$(dirname "$0")"

# --allow-fire is agency-only; strip it from static/adaptive.
_split_fire() {
  FIRE=()
  REST=()
  for a in "$@"; do
    if [[ "$a" == --allow-fire ]]; then FIRE+=("$a"); else REST+=("$a"); fi
  done
}

case "${1:-}" in
  up)        python3 rt.py smoke ;;
  smoke)     python3 rt.py smoke ;;
  static)    shift; python3 rt.py static "$@" ;;
  adaptive)  shift; python3 rt.py adaptive "$@" ;;
  agency)    shift; python3 rt.py agency "$@" ;;
  prompt)    shift; python3 rt.py prompt "$@" ;;
  full)
    shift
    _split_fire "$@"
    python3 rt.py static "${REST[@]}" || echo "[static failed]"
    python3 rt.py adaptive "${REST[@]}" || echo "[adaptive failed]"
    python3 rt.py agency "${REST[@]}" "${FIRE[@]}" || echo "[agency failed]"
    python3 rt.py report
    ;;
  report)    shift; python3 rt.py report "$@" ;;
  *)
    echo "usage: run.sh {up|smoke|static|adaptive|agency|prompt|full|report} [args]" >&2
    exit 2 ;;
esac
