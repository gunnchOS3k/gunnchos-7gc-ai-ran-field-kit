#!/usr/bin/env bash
set -euo pipefail
DRY=0; COND=""; IFACE=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY=1; shift;;
    --condition) COND="$2"; shift 2;;
    --interface) IFACE="$2"; shift 2;;
    *) echo "unknown arg $1"; exit 2;;
  esac
done
[[ -n "$COND" && -n "$IFACE" ]] || { echo "usage: $0 --condition <name> --interface <if> [--dry-run]"; exit 2; }
echo "target_interface=$IFACE condition=$COND dry_run=$DRY"
if [[ "$DRY" -eq 1 ]]; then
  echo "DRY-RUN: would apply shaping for $COND on $IFACE (no change)"
  exit 0
fi
if ! command -v tc >/dev/null 2>&1; then
  echo "BLOCKED: tc not available; cannot apply shaping on this host"
  exit 3
fi
# Minimal example — operator must confirm parameters from network_conditions.yaml
echo "HUMAN_ACTION_REQUIRED: confirm YAML params then run privileged tc netem"
exit 4
