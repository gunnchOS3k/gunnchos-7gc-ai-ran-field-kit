#!/usr/bin/env bash
# Thin wrapper: checkout locked siblings via Python helper.
# Token must be supplied by the workflow via PORTFOLIO_CHECKOUT_TOKEN (never echo).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPOS_ROOT="${1:-$(dirname "$ROOT")}"
OUT="${2:-$ROOT/orchestration/gates_4_6/locked_checkout_report.json}"
mkdir -p "$(dirname "$OUT")"
python3 "$ROOT/scripts/checkout_locked_repositories.py" \
  --lock "$ROOT/integration/repo-lock.json" \
  --repos-root "$REPOS_ROOT" \
  --output "$OUT"
