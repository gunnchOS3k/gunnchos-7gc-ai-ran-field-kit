#!/usr/bin/env bash
set -euo pipefail
IFACE=""
while [[ $# -gt 0 ]]; do case "$1" in --interface) IFACE="$2"; shift 2;; *) shift;; esac; done
[[ -n "$IFACE" ]] || { echo "need --interface"; exit 2; }
if command -v tc >/dev/null 2>&1; then
  echo "attempting tc qdisc del dev $IFACE root (may require sudo)"
  tc qdisc del dev "$IFACE" root 2>/dev/null || true
fi
echo "restore attempted for $IFACE"
