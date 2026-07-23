#!/usr/bin/env python3
"""Validate Gate 1 locked thesis document/JSON agreement."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_contract import validate_document  # noqa: E402

DOC = ROOT / "GATE1_LOCKED_RESEARCH_THESIS.md"
JSON_PATH = ROOT / "contracts" / "gate1_locked_thesis.v1.json"
SCHEMA = ROOT / "contracts" / "gate1_locked_thesis.v1.schema.json"

REQUIRED_REPOS = {
    "gunnchos-7gc-ai-ran-field-kit",
    "edge-io-measurement-node",
    "7gc-digital-twin",
    "spectrumx-ai-ran-gary",
    "ntn-resilience-sim",
}
OPTIONAL_REPO = "readygary-6g-beam-selection"


def evaluate(doc_path: Path = DOC, json_path: Path = JSON_PATH, schema_path: Path = SCHEMA) -> dict:
    errors: list[str] = []
    if not doc_path.is_file():
        return {"ok": False, "gate1_status": "FAIL", "errors": ["missing GATE1_LOCKED_RESEARCH_THESIS.md"]}
    if not json_path.is_file():
        return {"ok": False, "gate1_status": "FAIL", "errors": ["missing gate1_locked_thesis.v1.json"]}

    text = doc_path.read_text(encoding="utf-8")
    payload = json.loads(json_path.read_text(encoding="utf-8"))

    try:
        validate_document(
            payload,
            ROOT / "contracts",
            expected_schema_name="gunnchos.gate1_locked_thesis",
            enforce_privacy=False,
        )
    except Exception as exc:  # noqa: BLE001
        errors.append(f"schema validation failed: {exc}")

    title = payload.get("title") or ""
    hyp = payload.get("central_hypothesis") or ""
    rqs = payload.get("research_questions") or []
    papers = payload.get("papers") or []
    repos = payload.get("repositories") or []

    if text.count(title) < 1:
        errors.append("markdown document does not contain the exact locked title")
    if hyp not in text:
        errors.append("markdown document does not contain the exact central hypothesis")
    if len(rqs) != 3:
        errors.append(f"expected exactly 3 research questions, found {len(rqs)}")
    if len(papers) != 3:
        errors.append(f"expected exactly 3 papers, found {len(papers)}")
    if len({rq.get("id") for rq in rqs}) != 3:
        errors.append("research question IDs must be unique RQ1/RQ2/RQ3")

    # Count RQ headings in markdown to prevent silent fourth RQ
    rq_heads = re.findall(r"^### RQ\d+", text, flags=re.M)
    if len(rq_heads) != 3:
        errors.append(f"markdown must contain exactly three RQ headings, found {len(rq_heads)}")

    names = {r.get("name") for r in repos}
    for req in REQUIRED_REPOS:
        match = next((r for r in repos if r.get("name") == req), None)
        if not match:
            errors.append(f"missing required repository mapping: {req}")
        elif not match.get("required"):
            errors.append(f"repository must be required: {req}")
        elif not match.get("primary_questions"):
            errors.append(f"required repository missing primary_questions: {req}")

    opt = next((r for r in repos if r.get("name") == OPTIONAL_REPO), None)
    if not opt:
        errors.append("ReadyGary optional repository mapping missing")
    elif opt.get("required") is not False:
        errors.append("ReadyGary must be marked required=false")
    elif opt.get("primary_questions"):
        errors.append("ReadyGary must not own a primary RQ")

    non_goals = payload.get("non_goals") or []
    for needle in [
        "deployment-scale 6G",
        "live commercial NTN",
        "direct personal identifiers",
        "ReadyGary as required",
        "synthetic evidence as measured",
    ]:
        if not any(needle.lower() in g.lower() for g in non_goals):
            errors.append(f"non_goals missing expected theme: {needle}")

    ok = not errors
    status = "GATE_1_PASS" if ok else ("PARTIAL_NOT_FORMALLY_LOCKED" if payload else "FAIL")
    if ok:
        # Keep JSON status honest with validator
        if payload.get("gate1_status") != "GATE_1_PASS":
            errors.append("JSON gate1_status must be GATE_1_PASS when validator passes")
            ok = False
            status = "FAIL"

    return {
        "ok": ok,
        "gate1_status": status if ok else ("FAIL" if errors else status),
        "title": title,
        "research_question_count": len(rqs),
        "paper_count": len(papers),
        "repository_count": len(names),
        "errors": errors,
    }


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--doc", default=str(DOC))
    p.add_argument("--json", default=str(JSON_PATH))
    p.add_argument("--output", default=None)
    args = p.parse_args(argv)
    result = evaluate(Path(args.doc), Path(args.json))
    text = json.dumps(result, indent=2)
    print(text)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
    return 0 if result["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
