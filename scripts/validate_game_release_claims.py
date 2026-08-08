#!/usr/bin/env python3
"""Reject Beta/RC game release claims when blocks_token=true assets remain.

Cont V claim firewall. Primary surface is field-kit `game_release_matrix.yaml`.
When sibling `content/missing_assets.json` is present, it is the source of truth
for remaining blockers; otherwise matrix `blocks_token_assets_remaining` is used.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SIBLING = ROOT.parent
MATRIX = ROOT / "program" / "full_product" / "game_release_matrix.yaml"

GAME_REPOS = {
    "anime-aggressors": {
        "missing_assets": "content/missing_assets.json",
        "beta_token": "ANIME_BETA_CONTENT_COMPLETE_DIGITAL",
        "rc_token": "ANIME_DIGITAL_RC_READY",
        "matrix_key": "anime_aggressors",
        "status_docs": [
            "docs/ANIME_BETA_CONTENT_STATUS.md",
            "docs/ANIME_DIGITAL_RC_STATUS.md",
        ],
        "rc_evidence": "playtest-evidence/digital_rc_validation.json",
    },
}


def load_yaml(path: Path) -> Any:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def blocks_token_hits(path: Path) -> list[str]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items") or data.get("assets") or []
    hits: list[str] = []
    for item in items:
        if isinstance(item, dict) and item.get("blocks_token") is True:
            hits.append(str(item.get("id") or item.get("name") or item))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict-siblings",
        action="store_true",
        help="Also fail when sibling status docs still claim YES/token_earned",
    )
    args = parser.parse_args()

    errors: list[str] = []
    matrix = load_yaml(MATRIX) if MATRIX.exists() else {}
    games = (matrix or {}).get("games") or {}

    for repo, meta in GAME_REPOS.items():
        entry = games.get(meta["matrix_key"]) or {}
        missing = SIBLING / repo / meta["missing_assets"]
        hits = blocks_token_hits(missing)
        remaining = entry.get("blocks_token_assets_remaining")
        blocker_count = len(hits) if hits else int(remaining or 0)

        if blocker_count <= 0:
            continue

        if entry.get("content_complete") is True:
            errors.append(
                f"{repo}: content_complete=true while {blocker_count} blocks_token assets remain"
            )
        if entry.get("rc_digital") is True:
            errors.append(
                f"{repo}: rc_digital=true while {blocker_count} blocks_token assets remain"
            )

        tokens = entry.get("tokens") or {}
        for tok in (meta["beta_token"], meta["rc_token"]):
            validity = tokens.get(tok)
            if validity is None:
                # Matrix must record revoke when blockers known
                if remaining and int(remaining) > 0:
                    errors.append(
                        f"{repo}: missing tokens.{tok} while blocks_token_assets_remaining={remaining}"
                    )
                continue
            if validity != "PREMATURE_REVOKE":
                errors.append(
                    f"{repo}: tokens.{tok}={validity!r} while {blocker_count} "
                    "blocks_token assets remain; must be PREMATURE_REVOKE"
                )

        if args.strict_siblings and hits:
            for rel in meta.get("status_docs") or []:
                doc = SIBLING / repo / rel
                if not doc.exists():
                    continue
                text = doc.read_text(encoding="utf-8", errors="ignore")
                if "PREMATURE_REVOKE" in text or "REVOKED" in text:
                    continue
                if "**YES**" in text and meta["beta_token"] in text:
                    errors.append(
                        f"{repo}: {rel} still claims Beta token YES while blocks_token=true remains"
                    )
            rc_json = SIBLING / repo / meta.get("rc_evidence", "")
            if rc_json.exists():
                try:
                    payload = json.loads(rc_json.read_text(encoding="utf-8"))
                except json.JSONDecodeError:
                    payload = {}
                if payload.get("token_earned") is True:
                    errors.append(
                        f"{repo}: {meta['rc_evidence']} token_earned=true while "
                        "blocks_token=true assets remain"
                    )

    if errors:
        print("GAME_RELEASE_CLAIM_FIREWALL_FAIL")
        for e in errors[:50]:
            print(e)
        if len(errors) > 50:
            print(f"... and {len(errors) - 50} more")
        return 1

    print("GAME_RELEASE_CLAIM_FIREWALL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
